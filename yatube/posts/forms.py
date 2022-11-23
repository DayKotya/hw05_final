from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст'),
            'group': _('Группа'),
            'image': _('Изображение')
        }
        help_texts = {
            'text': _('Пишите сюда текст поста'),
            'group': _('Группа, которой будет принадлежать пост'),
            'image': _('Изображение к посту')
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Текст комментария'),
        }
        help_text = {
            'text': _('Пишите сюда текст комментария')
        }
