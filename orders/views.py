from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from .forms import CheckoutForm
from .models import Order, OrderItem
from paintings.models import Painting
from cart.views import _get_cart_session, _calculate_cart_totals
from cart.models import Coupon
import razorpay
from razorpay.errors import BadRequestError


def _get_razorpay_client():
    if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
        raise ValueError('Razorpay credentials are not configured. Please add RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET to your .env file.')
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def _get_customer_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.user.is_staff:
        return order
    if not request.user.is_authenticated or order.user != request.user:
        raise Http404('Order not found.')
    return order


def checkout_view(request):
    """Display checkout form with order summary"""
    cart = _get_cart_session(request)
    
    if not cart:
        return redirect('/cart/')
    
    # Build cart items for order summary
    cart_items = []
    for pid, qty in cart.items():
        try:
            painting = Painting.objects.get(pk=int(pid), status='published')
            order_price = painting.discount_price or painting.price
            subtotal = float(order_price) * qty
            cart_items.append({
                'painting': painting,
                'quantity': qty,
                'price': float(order_price),
                'subtotal': subtotal,
            })
        except Painting.DoesNotExist:
            continue
    
    coupon_code = request.session.get('coupon_code')
    totals = _calculate_cart_totals(cart_items, coupon_code)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order with required totals set up front
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                billing_address=form.cleaned_data['billing_address'],
                billing_city=form.cleaned_data['billing_city'],
                billing_state=form.cleaned_data['billing_state'],
                billing_postal_code=form.cleaned_data['billing_postal_code'],
                billing_country=form.cleaned_data['billing_country'],
                same_as_billing=form.cleaned_data['same_as_billing'],
                payment_method=form.cleaned_data['payment_method'],
                subtotal=totals['subtotal'],
                discount=totals['discount'],
                tax=totals['tax'],
                shipping_cost=totals['shipping'],
                total=totals['grand_total'],
                coupon_code=coupon_code or '',
            )
            
            # Shipping address
            if form.cleaned_data['same_as_billing']:
                order.shipping_address = form.cleaned_data['billing_address']
                order.shipping_city = form.cleaned_data['billing_city']
                order.shipping_state = form.cleaned_data['billing_state']
                order.shipping_postal_code = form.cleaned_data['billing_postal_code']
                order.shipping_country = form.cleaned_data['billing_country']
            else:
                order.shipping_address = form.cleaned_data['shipping_address']
                order.shipping_city = form.cleaned_data['shipping_city']
                order.shipping_state = form.cleaned_data['shipping_state']
                order.shipping_postal_code = form.cleaned_data['shipping_postal_code']
                order.shipping_country = form.cleaned_data['shipping_country']
            
            # Preserve totals after shipping info assignment
            order.subtotal = totals['subtotal']
            order.discount = totals['discount']
            order.tax = totals['tax']
            order.shipping_cost = totals['shipping']
            order.total = totals['grand_total']
            order.coupon_code = coupon_code or ''
            
            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    painting=item['painting'],
                    price=Decimal(str(item['price'])),
                    quantity=item['quantity']
                )
            
            order.save()
            
            # Clear cart and coupon
            request.session['cart'] = {}
            request.session['coupon_code'] = None
            request.session.modified = True
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
            # Redirect to payment based on method
            if order.payment_method == 'razorpay':
                return redirect('orders:razorpay_checkout', order_id=order.id)
            elif order.payment_method == 'stripe':
                return redirect('orders:stripe_checkout', order_id=order.id)
            else:  # cod
                return redirect('orders:order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'totals': totals,
    }
    
    return render(request, 'orders/checkout.html', context)


@login_required
def order_confirmation(request, order_id):
    """Display order confirmation page"""
    order = _get_customer_order(request, order_id)
    
    # For COD, mark as confirmed
    if order.payment_method == 'cod' and order.payment_status == 'pending':
        order.payment_status = 'completed'
        order.status = 'confirmed'
        order.save()
    
    return render(request, 'orders/order_confirmation.html', {'order': order})


@login_required
def order_list(request):
    if request.user.is_staff:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = _get_customer_order(request, pk)
    
    status_steps = [
        {'key': 'pending', 'label': 'Pending'},
        {'key': 'confirmed', 'label': 'Confirmed'},
        {'key': 'processing', 'label': 'Processing'},
        {'key': 'shipped', 'label': 'Shipped'},
        {'key': 'delivered', 'label': 'Delivered'},
    ]
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'status_steps': status_steps,
    })


@login_required
def cancel_order(request, order_id):
    order = _get_customer_order(request, order_id)

    if order.status in ['shipped', 'delivered', 'cancelled']:
        messages.warning(request, 'This order cannot be cancelled at this stage.')
    else:
        order.status = 'cancelled'
        if order.payment_status == 'completed':
            order.payment_status = 'refunded'
        order.notes = 'Order cancelled by customer.'
        order.save()
        messages.success(request, 'Your order has been cancelled successfully.')

    return redirect('orders:order_detail', pk=order.id)


@login_required
def track_order(request, order_id):
    order = _get_customer_order(request, order_id)

    status_steps = [
        {'key': 'pending', 'label': 'Pending'},
        {'key': 'confirmed', 'label': 'Confirmed'},
        {'key': 'processing', 'label': 'Processing'},
        {'key': 'shipped', 'label': 'Shipped'},
        {'key': 'delivered', 'label': 'Delivered'},
    ]
    return render(request, 'orders/order_tracking.html', {'order': order, 'status_steps': status_steps})


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    subject = f'Order Confirmation - FireworkArt #{order.id}'
    
    context = {
        'order': order,
        'site_name': 'FireworkArt',
    }
    
    html_message = render_to_string('orders/emails/order_confirmation.html', context)
    plain_message = render_to_string('orders/emails/order_confirmation.txt', context)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=True,
    )


@login_required
def razorpay_checkout(request, order_id):
    """Razorpay payment checkout page"""
    order = _get_customer_order(request, order_id)
    
    if order.payment_status == 'completed':
        return redirect('orders:order_confirmation', order_id=order.id)
    
    try:
        client = _get_razorpay_client()
        amount_paise = int(float(order.total) * 100)
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': str(order.id),
            'notes': {
                'order_id': str(order.id),
                'customer_email': order.email,
            }
        })
    except (BadRequestError, ValueError) as e:
        return render(request, 'orders/payment_failed.html', {'error': str(e)})
    except Exception as e:
        return render(request, 'orders/payment_failed.html', {'error': f'Unable to initiate Razorpay payment: {e}'})
    
    order.razorpay_order_id = razorpay_order['id']
    order.save()
    
    context = {
        'order': order,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount_paise,
    }
    
    return render(request, 'orders/razorpay_checkout.html', context)


@csrf_exempt
def razorpay_verify(request):
    """Verify Razorpay payment"""
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        order = None
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            client = _get_razorpay_client()
            
            # Verify signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            
            # Payment successful
            order.payment_status = 'completed'
            order.status = 'confirmed'
            order.razorpay_payment_id = razorpay_payment_id
            order.save()
            
            send_payment_confirmation_email(order)
            
            return redirect('orders:order_confirmation', order_id=order.id)
        except Order.DoesNotExist:
            return render(request, 'orders/payment_failed.html', {'error': 'Order not found for this Razorpay payment.'})
        except (BadRequestError, ValueError) as e:
            if order:
                order.payment_status = 'failed'
                order.save()
            return render(request, 'orders/payment_failed.html', {'error': str(e)})
        except Exception as e:
            if order:
                order.payment_status = 'failed'
                order.save()
            return render(request, 'orders/payment_failed.html', {'error': f'Payment verification failed: {e}'})
    
    return redirect('/cart/')


@login_required
def stripe_checkout(request, order_id):
    """Stripe payment checkout page"""
    order = _get_customer_order(request, order_id)
    
    if order.payment_status == 'completed':
        return redirect('orders:order_confirmation', order_id=order.id)
    
    context = {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    
    return render(request, 'orders/stripe_checkout.html', context)


def send_payment_confirmation_email(order):
    """Send payment confirmation email"""
    subject = f'Payment Confirmed - FireworkArt Order #{order.id}'
    
    context = {
        'order': order,
        'site_name': 'FireworkArt',
    }
    
    html_message = render_to_string('orders/emails/payment_confirmation.html', context)
    plain_message = render_to_string('orders/emails/payment_confirmation.txt', context)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [order.email],
        html_message=html_message,
        fail_silently=True,
    )


@login_required
def generate_invoice(request, order_id):
    """Generate and download PDF invoice"""
    order = _get_customer_order(request, order_id)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.units import inch
        from io import BytesIO
        from django.http import HttpResponse
    except ImportError:
        # Fallback to simple HTML view if reportlab not installed
        order = get_object_or_404(Order, pk=order_id)
        return render(request, 'orders/invoice.html', {'order': order})
    
    order = get_object_or_404(Order, pk=order_id)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"<b>Invoice #{order.id}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Order info
    order_info = Paragraph(
        f"<b>Order Date:</b> {order.created.strftime('%B %d, %Y')}<br/>"
        f"<b>Order Status:</b> {order.get_status_display()}<br/>"
        f"<b>Payment Status:</b> {order.get_payment_status_display()}",
        styles['Normal']
    )
    elements.append(order_info)
    elements.append(Spacer(1, 0.2*inch))
    
    # Customer info
    customer_info = Paragraph(
        f"<b>Bill To:</b><br/>"
        f"{order.full_name}<br/>"
        f"{order.billing_address}<br/>"
        f"{order.billing_city}, {order.billing_state} {order.billing_postal_code}<br/>"
        f"{order.billing_country}<br/>"
        f"Email: {order.email}<br/>"
        f"Phone: {order.phone}",
        styles['Normal']
    )
    elements.append(customer_info)
    elements.append(Spacer(1, 0.2*inch))
    
    # Items table
    items_data = [['Item', 'Quantity', 'Price', 'Subtotal']]
    for item in order.items.all():
        items_data.append([
            item.painting.title,
            str(item.quantity),
            f"${item.price}",
            f"${item.subtotal}"
        ])
    
    items_table = Table(items_data)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), (0.2, 0.2, 0.2)),
        ('TEXTCOLOR', (0, 0), (-1, 0), (1, 1, 1)),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), (0.9, 0.9, 0.9)),
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0))
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Totals
    totals_info = Paragraph(
        f"<b>Subtotal:</b> ${order.subtotal}<br/>"
        f"<b>Discount:</b> -${order.discount}<br/>"
        f"<b>Tax (10%):</b> ${order.tax}<br/>"
        f"<b>Shipping:</b> ${order.shipping_cost}<br/>"
        f"<b>Total:</b> ${order.total}",
        styles['Normal']
    )
    elements.append(totals_info)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{order.get_invoice_filename()}"'
    
    return response

