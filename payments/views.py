from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order


@csrf_exempt
def razorpay_verify(request):
    if request.method == 'POST':
        # Basic placeholder: mark order paid if `receipt` provided
        receipt = request.POST.get('razorpay_receipt') or request.POST.get('receipt')
        if receipt:
            try:
                order = Order.objects.get(pk=int(receipt))
                order.paid = True
                order.save()
                return render(request, 'shop/order_success.html', {'order': order})
            except Exception:
                pass
        return render(request, 'shop/order_failed.html')
    return redirect('product_list')
