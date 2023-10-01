from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count

from blog.models import Post, Category, Comment
from .forms import PostsForm, EditProfileForm, CommentsForm
from .redirects import redirect_with_id, redirect_with_username
from .paginator_for_posts import paginator_for_posts


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
    ).annotate(
        comment_count=Count('comments')
    )
    page_obj = paginator_for_posts(list_posts, request.GET.get('page'))
    context = {'page_obj': page_obj}
    template = 'blog/index.html'
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post,
        id=id,
    )
    if (post.author != request.user):
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
    page_obj = paginator_for_posts(post_list, request.GET.get('page'))
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def posts_create(request):
    form = PostsForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect_with_username(request.user.username)
    return render(request, 'blog/create.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    post_list = Post.objects.select_related().filter(
        author=profile
    ).annotate(
        comment_count=Count('comments')
    )
    page_obj = paginator_for_posts(post_list, request.GET.get('page'))
    context = {'profile': profile, 'page_obj': page_obj}
    template_name = 'blog/profile.html'
    return render(request, template_name, context)


@login_required
def edit_profile(request, username):
    instance = get_object_or_404(User, username=username)
    form = EditProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)


@login_required
def edit_post(request, id):
    instance = get_object_or_404(Post, id=id)
    if (instance.author != request.user):
        return redirect_with_id(id)
    form = PostsForm(
        request.POST or None,
        files=request.FILES or None,
        instance=instance
    )
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect_with_id(id)
    templates = 'blog/create.html'
    return render(request, templates, context)


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentsForm(request.POST or None)
    if form.is_valid:
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect_with_id(id)
    template = 'blog/comment.html'
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_comment(request, post_id, comment_id):
    instance = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id,
        author=request.user
        )
    form = CommentsForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect_with_id(post_id)
    context = {'form': form, 'comment': instance}
    template = 'blog/comment.html'
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    instance = get_object_or_404(Post, id=post_id, author=request.user)
    form = PostsForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    context = {'form': form}
    template = 'blog/create.html'
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    instance = get_object_or_404(Comment, id=comment_id, author=request.user)
    if request.method == 'POST':
        instance.delete()
        return redirect_with_id(post_id)
    context = {'comment': instance}
    template = 'blog/comment.html'
    return render(request, template, context)
