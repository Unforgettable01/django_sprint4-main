from django import forms

from .models import Post, User


class PostsForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = '__all__'
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'})
            }


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
