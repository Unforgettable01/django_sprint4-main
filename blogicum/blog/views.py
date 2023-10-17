from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import generic

from blog.models import Comment, Post, Category
from .forms import PostsForm, EditProfileForm, CommentsForm
from .redirects import redirect_with_id, redirect_with_username
from .paginator_for_posts import paginator_for_posts
from .get_objects import (get_user,
                          post_without_filters,
                          post_with_filters,
                          get_list_posts,
                          get_category,
                          get_comment
                          )


class IndexView(generic.ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = 'id'
    paginate_by = 10


def post_detail(request, id):
    post = post_without_filters(id)
    if (post.author != request.user):
        post = post_with_filters(id=id)
    comments = Comment.objects.select_related(
        'author'
    ).filter(
        post=post,
    )
    form = CommentsForm()
    context = {'post': post, 'form': form, 'comments': comments}
    template = 'blog/detail.html'
    return render(request, template, context)


""" def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_category(category_slug)
    post_list = post_with_filters()
    page_obj = paginator_for_posts(post_list, request.GET.get('page'))
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)
 """


class CategoryPostListView(generic.ListView):
    paginate_by = 10
    template_name = 'blog/category.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Post.objects.filter(
            category=get_category(self.kwargs['category_slug'])
            )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_category(self.kwargs['category_slug'])
        return context


""" @login_required
def posts_create(request):
    form = PostsForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect_with_username(request.user.username)
    return render(request, 'blog/create.html', context) """


class PostCreateView(generic.CreateView):
    model = Post
    form_class = PostsForm
    template_name = 'blog/create.html'
    # success_url = 'blog:profile'


def profile(request, username):
    profile = get_user(username)
    post_list = get_list_posts(profile)
    page_obj = paginator_for_posts(post_list, request.GET.get('page'))
    context = {'profile': profile, 'page_obj': page_obj}
    template_name = 'blog/profile.html'
    return render(request, template_name, context)


@login_required
def edit_profile(request, username):
    instance = get_user(username)
    form = EditProfileForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        form.save()
    template = 'blog/user.html'
    return render(request, template, context)


@login_required
def edit_post(request, id):
    instance = post_without_filters(id)
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
    post = post_without_filters(id)
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
    instance = get_comment(comment_id, post_id, request.user)
    form = CommentsForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect_with_id(post_id)
    context = {'form': form, 'comment': instance}
    template = 'blog/comment.html'
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    instance = post_without_filters(post_id, request.user)
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
