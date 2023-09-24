from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from blog.models import Post, Category


def index(request):

    list_posts = Post.objects.select_related(
        'author',
        'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )[:5]
    context = {'post_list': list_posts}
    template = 'blog/index.html'
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post,
        pk=id,
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )

    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
    post_list = Post.objects.select_related().filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category_id=category
    )
    context = {'category': category, 'post_list': post_list}
    return render(request, template, context)
