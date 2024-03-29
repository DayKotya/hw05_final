from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, где более 15 символов',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Отображение названий объектов правильные."""
        post = PostModelTest.post
        group = PostModelTest.group
        object_names = {
            post: post.text[:15],
            group: group.title
        }
        for model, expected_value in object_names.items():
            with self.subTest(model=model):
                self.assertEqual(model.__str__(), expected_value)
