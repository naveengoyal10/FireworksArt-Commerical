from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import CheckoutForm
from .models import Order, OrderItem
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.db.models.functions import Coalesce
from paintings.models import Painting, Category
import razorpay
from django.views.decorators.csrf import csrf_exempt


def product_list(request):
    query = request.GET.get('q', '')
    layout = request.GET.get('layout', 'grid')
    page = request.GET.get('page', 1)
    category_id = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    medium = request.GET.get('medium', '')
    size = request.GET.get('size', '')
    availability = request.GET.get('availability', '')
    sort = request.GET.get('sort', 'latest')

    products = Painting.objects.filter(status='published')

    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(artist_name__icontains=query) |
            Q(categories__name__icontains=query)
        ).distinct()

    if category_id:
        products = products.filter(categories__id=category_id).distinct()

    if medium:
        products = products.filter(medium__iexact=medium)

    if size:
        products = products.filter(size__iexact=size)

    if availability == 'available':
        products = products.filter(stock__gt=0)
    elif availability == 'unavailable':
        products = products.filter(stock__lte=0)

    try:
        if price_min:
            products = products.filter(price__gte=float(price_min))
    except ValueError:
        pass
    try:
        if price_max:
            products = products.filter(price__lte=float(price_max))
    except ValueError:
        pass

    products = products.annotate(price_value=Coalesce('discount_price', 'price'))
    if sort == 'price_low':
        products = products.order_by('price_value', '-created')
    elif sort == 'price_high':
        products = products.order_by('-price_value', '-created')
    else:
        products = products.order_by('-created')

    category_options = Category.objects.order_by('name')
    medium_options = Painting.objects.filter(status='published').values_list('medium', flat=True).distinct().exclude(medium='').order_by('medium')
    size_options = Painting.objects.filter(status='published').values_list('size', flat=True).distinct().exclude(size='').order_by('size')

    paginator = Paginator(products, 12)
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    context = {
        'products': products_page,
        'query': query,
        'layout': layout,
        'paginator': paginator,
        'page_obj': products_page,
        'category_options': category_options,
        'selected_category': category_id,
        'medium_options': [m for m in medium_options if m],
        'selected_medium': medium,
        'size_options': [s for s in size_options if s],
        'selected_size': size,
        'selected_availability': availability,
        'selected_sort': sort,
        'price_min': price_min,
        'price_max': price_max,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Painting, slug=slug, status='published')
    return render(request, 'shop/product_detail.html', {'product': product})


def _get_cart(request):
    return request.session.setdefault('cart', {})


def add_to_cart(request, product_id):
    cart = _get_cart(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session.modified = True
    return redirect('/cart/')


def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    return redirect('/cart/')


def cart_view(request):
    cart = _get_cart(request)
    items = []
    total = 0
    cleaned_cart = {}
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            continue
        subtotal = product.price * qty
        total += subtotal
        cleaned_cart[str(pid)] = qty
        items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})

    if cleaned_cart != cart:
        request.session['cart'] = cleaned_cart
        request.session.modified = True
        if not cleaned_cart:
            messages.error(request, 'Some cart items were no longer available and have been removed.')
            return redirect('product_list')
        messages.warning(request, 'Some unavailable items were removed from your cart.')

    return render(request, 'shop/cart.html', {'items': items, 'total': total})


def checkout(request):
    cart = _get_cart(request)
    if not cart:
        return redirect('product_list')

    valid_items = []
    cleaned_cart = {}
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            continue
        valid_items.append({'product': product, 'quantity': qty, 'subtotal': product.price * qty})
        cleaned_cart[str(pid)] = qty

    if cleaned_cart != cart:
        request.session['cart'] = cleaned_cart
        request.session.modified = True
        if not cleaned_cart:
            messages.error(request, 'Some items in your cart are no longer available. Your cart has been updated.')
            return redirect('/cart/')
        messages.warning(request, 'Some unavailable items were removed from your cart. Please review the updated cart.')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            if not valid_items:
                messages.error(request, 'Your cart is empty after removing unavailable items. Please add products before checking out.')
                return redirect('product_list')

            order = Order.objects.create(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
            )
            for item in valid_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['product'].price,
                    quantity=item['quantity'],
                )
            request.session['cart'] = {}
            request.session.modified = True
            return redirect(reverse('order_success', args=[order.id]))
    else:
        form = CheckoutForm()
    return render(request, 'shop/checkout.html', {'form': form, 'items': valid_items})


def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, 'shop/order_success.html', {'order': order})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def razorpay_checkout(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.paid:
        return redirect('order_success', order_id=order.id)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount = int(sum(item.price * item.quantity for item in order.items.all()) * 100)
    razorpay_order = client.order.create({'amount': amount, 'currency': 'INR', 'receipt': str(order.id)})
    return render(request, 'shop/razorpay_checkout.html', {
        'order': order,
        'razorpay_order': razorpay_order,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': amount,
    })


@csrf_exempt
def razorpay_verify(request):
    if request.method == 'POST':
        payload = request.POST
        razorpay_order_id = payload.get('razorpay_order_id')
        razorpay_payment_id = payload.get('razorpay_payment_id')
        razorpay_signature = payload.get('razorpay_signature')
        # find order by receipt (we used order.id as receipt)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })
        except Exception:
            return render(request, 'shop/order_failed.html')
        # mark order paid
        # retrieve receipt from order details
        r_order = client.order.fetch(razorpay_order_id)
        receipt = r_order.get('receipt')
        try:
            order = Order.objects.get(pk=int(receipt))
            order.paid = True
            order.save()
        except Exception:
            pass
        return render(request, 'shop/order_success.html', {'order': order})
    return redirect('product_list')
