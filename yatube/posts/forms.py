from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = (
            'text',
            'group',
            'image',
        )
        help_texts = {
            'text': _('Создайте свой пост!'),
            'group': _('Выберите группу!'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'form-control'})


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )
        help_texts = {
            'text': _('Оставьте свой комментарий')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs.update({'class': 'form-control'})
