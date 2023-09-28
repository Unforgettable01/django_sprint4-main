from django import forms

from .models import Post, User, Comment


class PostsForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
            }


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentsForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
