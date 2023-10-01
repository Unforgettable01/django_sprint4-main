from django.shortcuts import redirect


def redirect_with_id(pk):
    return redirect('blog:post_detail', pk)


def redirect_with_username(username):
    return redirect('blog:profile', username)
