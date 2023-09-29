from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from blog.models import Post, Category, Comment
from django.core.paginator import Paginator
from django.contrib.auth.models import User

from .forms import PostsForm, EditProfileForm, CommentsForm


def index(request):

    list_posts = Post.objects.select_related(
        'author',
        'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    ).order_by(
        'id'
    )
    paginator = Paginator(list_posts, 11)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
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
    comments = Comment.objects.select_related(
        'author'
    ).filter(
        post=post,
    )
    form = CommentsForm()
    context = {'post': post, 'form': form, 'comments': comments}
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
    ).order_by(
        'id'
    )
    paginator = Paginator(post_list, 11)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


def posts_create(request):
    form = PostsForm(request.POST or None)
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
    return render(request, 'blog/create.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related().filter(
        author=profile
    )
    context = {'profile': profile, 'page_obj': post_list}
    template_name = 'blog/profile.html'
    return render(request, template_name, context)


def edit_profile(request, username):
    instance = get_object_or_404(User, username=username)
    form = EditProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)


def edit_post(request, id):
    instance = get_object_or_404(Post, id=id)
    if (instance.author != request.user):
        return redirect('blog:post_detail', id=id)
    form = PostsForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=id)
    templates = 'blog/create.html'
    return render(request, templates, context)


def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentsForm(request.POST)
    if form.is_valid:
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=id)


def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    form = CommentsForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    context = {'form': form, 'comment': instance}
    template = 'blog/comment.html'
    return render(request, template, context)


def delete_post(request, post_id):
    instance = get_object_or_404(Post, id=post_id)
    form = PostsForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    context = {'form': form}
    template = 'blog/create.html'
    return render(request, template, context)
