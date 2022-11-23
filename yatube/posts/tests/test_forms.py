import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.post_author = Client()
        self.post_author.force_login(self.post.author)

    def test_create_post(self):
        """Тест создания поста."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        posts_count = Post.objects.count()
        response = self.post_author.post(
            reverse('posts:post_create'),
            data={
                'text': 'Текст нового поста',
                'group': PostCreateFormTests.group.id,
                'image': uploaded
            },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(Post.objects.get(pk=2).text, 'Текст нового поста')
        self.assertEqual(
            Post.objects.get(pk=2).group,
            PostCreateFormTests.group)
        self.assertTrue(
            Post.objects.filter(
                text='Текст нового поста',
                group=PostCreateFormTests.group.id,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """Тест редактирования поста."""
        another_group = Group.objects.create(
            title='Другая группа',
            slug='another-group',
            description='Описание другой группы'
        )
        response = self.post_author.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostCreateFormTests.post.id}),
            data={
                'text': 'Отредактированный текст поста',
                'group': another_group.id,
            },
            follow=True
        )
        post = Post.objects.get(id=PostCreateFormTests.post.id)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post.group, another_group)
        self.assertEqual(post.text, 'Отредактированный текст поста')
