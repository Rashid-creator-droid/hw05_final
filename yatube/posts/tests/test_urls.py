from http import HTTPStatus
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username='auth',
                email='example@gmail.com',
                password='password',
            ),
            text='Test text',
        )
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_home_and_group(self):
        """Страницы доступны всем"""
        url_names = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post.author}),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
        )
        for urls in url_names:
            with self.subTest():
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_for_authorized(self):
        """Страница create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_only_page(self):
        """Страница редактирования поста доступна только автору."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_uses_correct_urls(self):
        """Reverse возвращает ожидаемые url"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        page_names = {
            reverse(
                'posts:index'
            ): '/',
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug},
            ): f'/group/{self.group.slug}/',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username},
            ): f'/profile/{self.post.author}/',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            ): f'/posts/{self.post.pk}/',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk},
            ): f'/posts/{self.post.pk}/edit/',
            reverse(
                'posts:post_create'
            ): '/create/',
        }
        for views, urls in page_names.items():
            with self.subTest(views=views):
                self.assertURLEqual(views, urls)

    def test_redirect_anonymous_on_login(self):
        """
        Страницы перенаправят не зарегестрированного пользователя
        на страницу логина.
        """
        page_name = {
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ): urljoin(
                reverse('login'),
                f'?next=/posts/{self.post.pk}/comment/'
            ),
            reverse(
                'posts:post_create'
            ): urljoin(
                reverse('login'),
                '?next=/create/'
            ),
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post.author},
            ): urljoin(
                reverse('login'),
                f'?next=/profile/{self.post.author}/follow/',
            ),
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post.author},
            ): urljoin(
                reverse('login'),
                f'?next=/profile/{self.post.author}/unfollow/',
            ),
        }
        for url, url_2 in page_name.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, url_2)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        templates_url_names = {
            '': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        """Несуществующая страница вернет ошибку 404 с кастомным шаблоном"""
        response = self.guest_client.get('/nonexist-page/')
        template = 'core/404.html'
        self.assertTemplateUsed(
            response,
            template,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
        )
