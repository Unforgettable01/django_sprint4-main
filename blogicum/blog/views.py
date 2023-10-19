from django.utils import timezone
from typing import Any
from django.db import models
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
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


class PostDetailView(generic.DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_object(self):
        object = get_object_or_404(Post.objects.select_related(
            'location',
            'author',
        ).order_by(
            '-pub_date',
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ), pk=self.kwargs['id']
        )
        return object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        context['comments'] = self.object.comments.all
        return context


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


class PostCreateView(generic.CreateView):
    model = Post
    form_class = PostsForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
            )


class PostUpdateView(generic.UpdateView):
    model = Post
    form_class = PostsForm
    template_name = 'blog/create.html'

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
            )
    pk_url_kwarg = 'id'


class ProfileView(generic.ListView):
    paginate_by = 10
    model = Post
    template_name = 'blog/profile.html'

    def get_queryset(self) -> QuerySet[Any]:
        posts = get_list_posts(get_user(self.request.user))
        return posts

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_user(self.request.user)
        return context


class ProfileUpdateView(generic.UpdateView, LoginRequiredMixin, ):
    model = User
    form_class = EditProfileForm
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(
            username=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDeleteView(
        generic.DeleteView, UserPassesTestMixin, LoginRequiredMixin):
    model = Post
    form_class = PostsForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostsForm(self.request.POST or None,
                                    instance=context['post'])
        return context

    def test_func(self):
        object = self.get_object()
        if object.author != self.request.user:
            return False
        return True

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs.get(self.pk_url_kwarg)
        )


class CommentCreateView(generic.CreateView, LoginRequiredMixin):
    model = Post
    form_class = CommentsForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = get_object_or_404(Post.objects.select_related(
            'location',
            'author',
        ).order_by(
            '-pub_date',
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ), pk=self.kwargs['id']
        )
        comment.author = self.request.user
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['id']}
        )


class CommentUpdateView(generic.UpdateView, UserPassesTestMixin, LoginRequiredMixin):
    model = Comment
    form_class = CommentsForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        if object.author != self.request.user:
            return False
        return True

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs.get(self.pk_url_kwarg)
        )
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['post_id']}
        )


class CommentDeleteView(generic.DeleteView, UserPassesTestMixin, LoginRequiredMixin,):
    model = Comment
    form_class = CommentsForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        object = self.get_object()
        if object.author != self.request.user:
            return False
        return True

    def handle_no_permission(self):
        return redirect(
            'blog:post_detail',
            self.kwargs.get(self.pk_url_kwarg)
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs['post_id']}
        )
