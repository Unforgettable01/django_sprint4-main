from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
        ),
    path('posts/create/', views.posts_create, name='create_post'),
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
]
