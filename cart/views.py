from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from paintings.models import Painting
from .models import Coupon


SHIPPING_CHARGE = Decimal('10.00')
TAX_RATE = Decimal('0.10')  # 10% tax


def _get_cart_session(request):
    return request.session.setdefault('cart', {})


def _get_saved_items(request):
    return request.session.setdefault('saved_items', {})


def _calculate_cart_totals(cart_items, coupon_code=None):
    subtotal = sum(Decimal(str(item['subtotal'])) for item in cart_items)
    discount = Decimal('0')
    
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            if coupon.discount_type == 'percentage':
                discount = subtotal * (Decimal(str(coupon.value)) / 100)
            else:
                discount = min(Decimal(str(coupon.value)), subtotal)
        except Coupon.DoesNotExist:
            pass
    
    after_discount = subtotal - discount
    tax = after_discount * TAX_RATE
    shipping = SHIPPING_CHARGE if after_discount > 0 else Decimal('0')
    grand_total = after_discount + tax + shipping
    
    return {
        'subtotal': subtotal,
        'discount': discount,
        'after_discount': after_discount,
        'tax': tax,
        'shipping': shipping,
        'grand_total': grand_total,
    }


def add_to_cart(request, painting_id):
    cart = _get_cart_session(request)
    painting = get_object_or_404(Painting, pk=painting_id, status='published')
    
    cart[str(painting_id)] = cart.get(str(painting_id), 0) + 1
    request.session.modified = True
    
    next_url = request.GET.get('next', '/cart/')
    return redirect(next_url)


def remove_from_cart(request, painting_id):
    cart = _get_cart_session(request)
    cart.pop(str(painting_id), None)
    request.session.modified = True
    return redirect('/cart/')


def update_quantity(request, painting_id):
    if request.method == 'POST':
        cart = _get_cart_session(request)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            cart[str(painting_id)] = quantity
        else:
            cart.pop(str(painting_id), None)
        
        request.session.modified = True
    
    return redirect('/cart/')


def save_for_later(request, painting_id):
    cart = _get_cart_session(request)
    saved = _get_saved_items(request)
    
    # Move from cart to saved
    if str(painting_id) in cart:
        saved[str(painting_id)] = cart.pop(str(painting_id))
    
    request.session.modified = True
    return redirect('/cart/')


def move_to_cart(request, painting_id):
    saved = _get_saved_items(request)
    cart = _get_cart_session(request)
    
    # Move from saved to cart
    if str(painting_id) in saved:
        qty = saved.pop(str(painting_id))
        cart[str(painting_id)] = cart.get(str(painting_id), 0) + qty
    
    request.session.modified = True
    return redirect('/cart/')


def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        request.session['coupon_code'] = coupon_code if coupon_code else None
        request.session.modified = True
    
    return redirect('/cart/')


def cart_view(request):
    cart = _get_cart_session(request)
    saved = _get_saved_items(request)
    coupon_code = request.session.get('coupon_code')
    coupon_obj = None
    coupon_error = None
    
    # Validate coupon
    if coupon_code:
        try:
            coupon_obj = Coupon.objects.get(code=coupon_code, active=True)
        except Coupon.DoesNotExist:
            coupon_error = 'Invalid or expired coupon code'
            coupon_code = None
            request.session['coupon_code'] = None
            request.session.modified = True
    
    # Build cart items
    items = []
    for pid, qty in cart.items():
        try:
            painting = Painting.objects.get(pk=int(pid))
            order_price = painting.discount_price or painting.price
            subtotal = float(order_price) * qty
            items.append({
                'painting': painting,
                'quantity': qty,
                'price': float(order_price),
                'subtotal': subtotal,
            })
        except Painting.DoesNotExist:
            continue
    
    # Build saved items
    saved_items = []
    for pid, qty in saved.items():
        try:
            painting = Painting.objects.get(pk=int(pid))
            order_price = painting.discount_price or painting.price
            subtotal = float(order_price) * qty
            saved_items.append({
                'painting': painting,
                'quantity': qty,
                'price': float(order_price),
                'subtotal': subtotal,
            })
        except Painting.DoesNotExist:
            continue
    
    # Calculate totals
    totals = _calculate_cart_totals(items, coupon_code)
    
    context = {
        'items': items,
        'saved_items': saved_items,
        'coupon_code': coupon_code,
        'coupon_obj': coupon_obj,
        'coupon_error': coupon_error,
        'totals': totals,
    }
    
    return render(request, 'cart/cart.html', context)
