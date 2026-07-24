from django.shortcuts import get_object_or_404, redirect, render
from paintings.models import Painting


def _get_wishlist(request):
    return request.session.setdefault('wishlist', [])


def _get_cart_session(request):
    return request.session.setdefault('cart', {})


def wishlist_view(request):
    wishlist_ids = _get_wishlist(request)
    paintings = Painting.objects.filter(id__in=wishlist_ids, status='published')
    return render(request, 'wishlist/list.html', {'paintings': paintings})


def add_to_wishlist(request, painting_id):
    painting = get_object_or_404(Painting, id=painting_id, status='published')
    wishlist = _get_wishlist(request)
    if painting_id not in wishlist:
        wishlist.append(painting_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER', painting.get_absolute_url()))


def remove_from_wishlist(request, painting_id):
    wishlist = _get_wishlist(request)
    if painting_id in wishlist:
        wishlist.remove(painting_id)
        request.session['wishlist'] = wishlist
        request.session.modified = True
    return redirect('wishlist:wishlist_view')


def move_to_cart(request, painting_id):
    wishlist = _get_wishlist(request)
    if painting_id in wishlist:
        wishlist.remove(painting_id)
        request.session['wishlist'] = wishlist

    cart = _get_cart_session(request)
    cart[str(painting_id)] = cart.get(str(painting_id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart:cart_view')
