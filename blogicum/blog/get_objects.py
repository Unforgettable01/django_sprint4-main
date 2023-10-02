from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Category, User, Post, Comment


def get_user(username):
    return get_object_or_404(User, username=username)


def post_without_filters(pk, author=None):
    if author:
        return get_object_or_404(Post, pk=pk, author=author)
    return get_object_or_404(Post, pk=pk)


def filter_for_post(posts):
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now(),
    )


def post_with_filters(id=None):
    if id:
        post = filter_for_post(Post.objects)
        return get_object_or_404(post, pk=id)
    return filter_for_post(get_list_posts())


def get_list_posts(author=None):
    list_posts = Post.objects.select_related(
        'location',
        'author',
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')
    if author:
        return filter_author_for_post(list_posts, author)
    return list_posts


def filter_author_for_post(posts, author):
    return posts.filter(
        author=author
        )


def get_comment(comment_id, post_id, author):
    return get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id,
        author=author)


def get_category(category_slug):
    return get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True)
