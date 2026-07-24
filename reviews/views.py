from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from paintings.models import Painting
from .forms import ReviewForm
from .models import Review, ReviewImage


def review_list(request):
    reviews = Review.objects.filter(active=True).select_related('painting', 'user')
    return render(request, 'reviews/list.html', {'reviews': reviews})


@login_required(login_url='/accounts/login/')
def add_review(request, painting_id):
    painting = get_object_or_404(Painting, pk=painting_id, status='published')

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.painting = painting
            review.user = request.user
            review.active = False
            review.save()

            for uploaded_image in request.FILES.getlist('images'):
                ReviewImage.objects.create(review=review, image=uploaded_image)

            messages.success(request, 'Thank you for your review. It will appear once approved by an administrator.')
        else:
            messages.error(request, 'There was a problem with your review submission. Please check the fields and try again.')

    return redirect(painting.get_absolute_url())
