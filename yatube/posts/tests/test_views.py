import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from http import HTTPStatus

from posts.models import Post, Group, Comment, Follow
from posts.forms import PostForm

User = get_user_model()

POSTS_NUMBER = 15

POSTS_ON_FIRST_PAGE = 10

POSTS_ON_SECOND_PAGE = POSTS_NUMBER - POSTS_ON_FIRST_PAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
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
            group=cls.group,
            image=uploaded
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post_author = Client()
        self.post_author.force_login(self.post.author)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTests.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTests.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Главная страница имеет правильный контекст."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_post = response.context['page_obj'][0]
        post_text = first_post.text
        post_author = first_post.author
        post_group = first_post.group
        post_image = first_post.image
        self.assertEqual(post_text, PostViewsTests.post.text)
        self.assertEqual(post_author, PostViewsTests.post.author)
        self.assertEqual(post_group, PostViewsTests.post.group)
        self.assertEqual(post_image, PostViewsTests.post.image)

    def test_group_list_page_show_correct_context(self):
        """Страницы группы имеет правильный контекст."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostViewsTests.group.slug})
        )
        first_post = response.context['page_obj'][0]
        group = response.context['group']
        post_text = first_post.text
        post_author = first_post.author
        post_image = first_post.image
        self.assertEqual(post_text, PostViewsTests.post.text)
        self.assertEqual(post_author, PostViewsTests.post.author)
        self.assertEqual(group, PostViewsTests.post.group)
        self.assertEqual(post_image, PostViewsTests.post.image)

    def test_profile_page_show_correct_context(self):
        """Страница профиля имеет правильный контекст."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostViewsTests.user}
            )
        )
        first_post = response.context['page_obj'][0]
        username = response.context['username']
        post_text = first_post.text
        post_author = first_post.author
        posts_number = response.context['posts_number']
        post_image = first_post.image
        self.assertEqual(post_text, PostViewsTests.post.text)
        self.assertEqual(post_author, PostViewsTests.post.author)
        self.assertEqual(username, PostViewsTests.post.author)
        self.assertEqual(post_image, PostViewsTests.post.image)
        self.assertEqual(posts_number, self.post.author.posts.count())

    def test_post_detail_page_show_correct_context(self):
        """Страница поста имеет правильный контекст."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostViewsTests.post.id}
            )
        )
        post = response.context['post']
        count_posts = response.context['count_posts']
        post_image = post.image
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post_image, PostViewsTests.post.image)
        self.assertEqual(count_posts, self.post.author.posts.count())

    def test_create_post_page_show_correct_context(self):
        """Страница создания поста имеет правильный контекст."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        is_edit = response.context['is_edit']
        self.assertFalse(is_edit)

    def test_edit_post_page_show_correct_context(self):
        """Страница редактирования поста имеет правильный контекст."""
        response = self.post_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostViewsTests.post.id}
            )
        )
        post = response.context['post']
        form = response.context['form']
        is_edit = response.context['is_edit']
        self.assertEqual(post.id, self.post.id)
        self.assertIsInstance(form, PostForm)
        self.assertTrue(is_edit)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        i = 0
        for i in range(POSTS_NUMBER):
            cls.post = Post.objects.create(
                text='Текст тестового поста',
                group=cls.group,
                author=cls.user
            )
            i += 1

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)
        cache.clear()

    def test_paginator_index(self):
        """Тест паджинатора главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']),
                         POSTS_ON_SECOND_PAGE)

    def test_paginator_group_list(self):
        """Тест паджинатора страницы группы."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']),
                         POSTS_ON_SECOND_PAGE)

    def test_paginator_profile(self):
        """Тест паджинатора страницы профиля."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user}
            )
        )
        self.assertEqual(len(response.context['page_obj']),
                         POSTS_ON_FIRST_PAGE)
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']),
                         POSTS_ON_SECOND_PAGE)

    def test_created_post_appears_on_related_pages(self):
        """Созданный пользователем пост появляется на

        главной странице,
        на странице группы,
        на странице пользователя,
        но не появляется на странице другой группы.
        """
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data={
                'text': 'Текст нового поста',
                'group': PaginatorViewsTest.group.id
            },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.get(pk=16)
        index_page = self.authorized_client.get(reverse('posts:index'))
        post_on_index = index_page.context['page_obj'][0]
        self.assertEqual(post, post_on_index)
        group_page = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug})
        )
        post_on_group_page = group_page.context['page_obj'][0]
        self.assertEqual(post, post_on_group_page)
        profile_page = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user}
            )
        )
        post_on_profile_page = profile_page.context['page_obj'][0]
        self.assertEqual(post, post_on_profile_page)
        another_group = Group.objects.create(
            title='Группа, в которой поста быть не должно',
            slug='another-group',
        )
        another_group_page = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': another_group.slug})
        )
        another_group_posts = another_group_page.context['page_obj']
        self.assertNotIn(post, another_group_posts)

    def test_created_comment_appears_on_related_page(self):
        """Созданный пользователем комментарий появляется на странице поста."""
        response = self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': PaginatorViewsTest.post.id}),
            data={
                'text': 'Текст комментария'
            },
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comment = Comment.objects.get(pk=1)
        comment_on_post_page = response.context['comments'][0]
        self.assertEqual(comment.text, comment_on_post_page.text)

    def test_index_cache(self):
        """Тест кэша."""
        response = self.authorized_client.get(reverse('posts:index'))
        have_cache = response.content
        one_post = Post.objects.get(id=10)
        one_post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        saved_cache = response.content
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        after_clearing_cache = response.content
        self.assertEqual(have_cache, saved_cache)
        self.assertNotEqual(saved_cache, after_clearing_cache)

    def test_follow_for_authorized_user(self):
        """Авторизованный юзер может подписываться на других пользователей."""
        author = User.objects.create_user(username='meepo')
        followings_count = Follow.objects.filter(
            user=PaginatorViewsTest.user,
        ).count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': author.username}))
        self.assertEqual(
            Follow.objects.filter(user=PaginatorViewsTest.user).count(),
            followings_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unfollow_for_authorized_user(self):
        """Авторизованный юзер может отписываться от других пользователей."""
        author = User.objects.create_user(username='meepo')
        first_count = Follow.objects.filter(
            user=PaginatorViewsTest.user,
        ).count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': author.username}))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        second_count = Follow.objects.filter(
            user=PaginatorViewsTest.user,
        ).count()
        response = self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': author.username}))
        third_count = Follow.objects.filter(
            user=PaginatorViewsTest.user,
        ).count()
        self.assertEqual(first_count, third_count)
        self.assertNotEqual(first_count, second_count)

    def test_author_posts_appear_on_related_pages(self):
        author = User.objects.create_user(username='meepo')
        author_post = Post.objects.create(text='Текст', author=author)
        subscribed_person = User.objects.create_user(username='sub')
        self.authorized_client.force_login(subscribed_person)
        response = self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': author.username}))
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        index_post = response.context['page_obj'][0]
        self.assertEqual(index_post, author_post)
        non_subscribed_person = PaginatorViewsTest.user
        self.authorized_client.force_login(non_subscribed_person)
        response = self.authorized_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(author_post, PaginatorViewsTest.post)
