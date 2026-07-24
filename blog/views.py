import json
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CommentForm
from .models import Category, Post, Tag


def post_list(request):
    posts = Post.objects.filter(published=True)
    categories = Category.objects.filter(active=True)
    tags = Tag.objects.all()
    return render(request, 'blog/list.html', {
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'page_title': 'Blog',
        'meta_title': 'Blog | Handmade Paintings',
        'meta_description': 'Read the Handmade Paintings blog for art inspiration, artist stories, and expert tips on choosing original artwork.',
        'og_type': 'website',
    })


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug, active=True)
    posts = Post.objects.filter(published=True, categories=category)
    categories = Category.objects.filter(active=True)
    tags = Tag.objects.all()
    return render(request, 'blog/list.html', {
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'page_title': f"Category: {category.name}",
        'page_description': category.description,
        'meta_title': f"{category.name} Articles | Handmade Paintings",
        'meta_description': category.description or f"Browse handmade painting articles in the {category.name} category.",
        'og_type': 'website',
    })


def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(published=True, tags=tag)
    categories = Category.objects.filter(active=True)
    tags = Tag.objects.all()
    return render(request, 'blog/list.html', {
        'posts': posts,
        'categories': categories,
        'tags': tags,
        'page_title': f"Tag: {tag.name}",
        'page_description': f"Browse handmade painting articles tagged with {tag.name}.",
        'meta_title': f"Tag: {tag.name} | Handmade Paintings",
        'meta_description': f"Browse handmade painting articles tagged with {tag.name}.",
        'og_type': 'website',
    })


def post_detail(request, year, month, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        published=True,
        published_date__year=year,
        published_date__month=month,
    )
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.user = request.user
            comment.active = False
            comment.save()
            messages.success(request, 'Thank you! Your comment has been submitted and will appear after admin approval.')
            return redirect(post.get_absolute_url())
        else:
            messages.error(request, 'There was a problem submitting your comment. Please check the form and try again.')

    comments = post.comments.filter(active=True).select_related('user')
    categories = Category.objects.filter(active=True)
    tags = Tag.objects.all()

    structured_data = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'BlogPosting',
        'headline': post.title,
        'image': [post.featured_image.url] if post.featured_image else [],
        'datePublished': post.published_date.isoformat(),
        'description': post.meta_description or post.excerpt,
        'mainEntityOfPage': {
            '@type': 'WebPage',
            '@id': request.build_absolute_uri(request.path)
        }
    })

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'categories': categories,
        'tags': tags,
        'meta_title': post.seo_title or post.title,
        'meta_description': post.meta_description or post.excerpt,
        'meta_image': post.featured_image.url if post.featured_image else None,
        'og_type': 'article',
        'structured_data': structured_data,
    })
