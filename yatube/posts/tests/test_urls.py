from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.user_2 = User.objects.create_user(username='user_2')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.not_author = Client()
        self.not_author.force_login(PostURLTests.user_2)

    def test_url_existion_for_non_authorized_person(self):
        """Тест адресов для неавторизованного пользователя."""
        responses_to_pages = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
            f'/posts/{PostURLTests.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND
        }
        for url, expected_response in responses_to_pages.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expected_response)

    def test_post_edit_url_existion_for_post_author(self):
        """Автор может зайти на страницу редактирования своего поста."""
        url = f'/posts/{PostURLTests.post.id}/edit/'
        response = self.authorized_client.get(url)
        expected_response = HTTPStatus.OK
        self.assertEqual(response.status_code, expected_response)

    def test_post_create_url_existion_for_authorized_user(self):
        """Авторизованный пользователь может создать пост."""
        url = '/create/'
        response = self.authorized_client.get(url)
        expected_response = HTTPStatus.OK
        self.assertEqual(response.status_code, expected_response)

    def test_comment_create_url_existion_for_authorized_user(self):
        """Авторизованный пользователь может комментировать пост."""
        url = f'/posts/{PostURLTests.post.id}/comment/'
        response = self.authorized_client.get(url)
        expected_response = HTTPStatus.FOUND
        self.assertEqual(response.status_code, expected_response)

    def test_post_edit_url_redirect_anonymous_on_post_detail(self):
        """Неавторизованный пользователь

        перенаправляется на подробности о посте
        при попытке отредактировать его.
        """
        url = f'/posts/{PostURLTests.post.id}/edit/'
        redirection_url = f'/posts/{PostURLTests.post.id}/'
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(
            response, redirection_url
        )

    def test_post_edit_url_redirect_anonymous_on_post_detail(self):
        """Неавторизованный пользователь

        перенаправляется на страницу авторизации
        при попытке создать его.
        """
        url = '/create/'
        redirection_url = '/auth/login/?next=/create/'
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(
            response, redirection_url
        )

    def test_post_edit_url_redirect_not_author_on_post_detail(self):
        """Не автор перенаправляется

        на подробности о посте
        при попытке отредактировать его.
        """
        url = f'/posts/{PostURLTests.post.id}/edit/'
        redirection_url = f'/posts/{PostURLTests.post.id}/'
        response = self.not_author.get(url, follow=True)
        self.assertRedirects(
            response, redirection_url
        )

    def test_post_urls_use_correct_template(self):
        """Адреса используют правильные шаблоны."""
        url_to_template = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/404/': 'core/404.html'
        }
        for url, template in url_to_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
