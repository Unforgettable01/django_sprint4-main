from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostListView.as_view(),
        name='category_posts'
        ),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('profile/<username>/', views.profile, name='profile'),
    path(
        'profile/<username>/edit/',
        views.edit_profile,
        name='edit_profile'
    ),
    path(
        'posts/<int:id>/edit/',
        views.edit_post,
        name='edit_post'
    ),
    path(
        'posts/<int:id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        views.edit_comment,
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.delete_post,
        name='delete_post'
    ),
    path(
        'posts/<post_id>/delete_comment/<comment_id>/',
        views.delete_comment,
        name='delete_comment'
    ),
]
