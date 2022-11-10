import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()
FIRST_NUMBER = 0
PAGE_SIZE = 10
SECOND_PAGE_SIZE = 5
ALL_PAGE_SIZE = PAGE_SIZE + SECOND_PAGE_SIZE
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED = SimpleUploadedFile(
    name='test_image.gif',
    content=SMALL_GIF,
    content_type='image/test',
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(
                username='auth',
                email='example@gmail.com',
                password='testpass',
            ),
            text='Test text',
            group=Group.objects.create(
                title='Test title',
                slug='Test_slug',
            ),
            image=UPLOADED,
        )
        cls.group = Group.objects.create(
            title='Test title 2',
            slug='test_slug_2',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse(
                'posts:index'
            ): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.post.group.slug},
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk},
            ): 'posts/create_post.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][FIRST_NUMBER]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        post_image = first_object.image
        self.assertEqual(post_image, self.post.image)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_group_0, self.post.group.title)

    def test_group_post_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.post.group.slug},
            )
        )
        first_object = response.context['group']
        group_title = first_object.title
        group_slug = first_object.slug
        post_image = Post.objects.first().image
        self.assertEqual(post_image, self.post.image)
        self.assertEqual(group_title, self.post.group.title)
        self.assertEqual(group_slug, self.post.group.slug)

    def test_post_not_in_another_group(self):
        """Post соотвествует своей группе"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.post.group.slug},
            )
        )
        first_object = response.context['group']
        post_slug_0 = first_object.slug
        self.assertNotEqual(post_slug_0, self.group.slug)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username},
            )
        )
        first_object = response.context['page_obj'][FIRST_NUMBER]
        post_author_0 = response.context['author'].username
        post_text_0 = first_object.text
        post_image = first_object.image
        self.assertEqual(post_image, self.post.image)
        self.assertEqual(post_author_0, self.post.author.username)
        self.assertEqual(post_text_0, self.post.text)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        first_object = response.context['posts']
        post_text = first_object.text
        post_image = first_object.image
        self.assertEqual(post_image, self.post.image)
        self.assertEqual(post_text, self.post.text)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post.author)
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = []
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(slug='test_slug')
        for index in range(ALL_PAGE_SIZE):
            cls.post.append(
                Post(
                    text=f'Test text {index}',
                    author=cls.user,
                    group=cls.group,
                )
            )
        Post.objects.bulk_create(cls.post)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

    def test_first_page(self):
        """Выведено нужное количество постов на 1 страницу"""
        url_names = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user}),
        )
        for urls in url_names:
            response = self.client.get(urls)
            self.assertEqual(
                len(response.context.get('page_obj').object_list),
                PAGE_SIZE,
            )

    def test_second_page(self):
        """Выведено нужное количество постов на последеней странице"""
        url_names = (
            reverse(
                'posts:index'
            ),
            reverse(
                'posts:group_posts',
                kwargs={'slug': self.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user},
            ),
        )
        for urls in url_names:
            response = self.client.get(urls, {'page': 2})
            self.assertEqual(
                len(response.context.get('page_obj').object_list),
                SECOND_PAGE_SIZE,
            )


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()

    def test_cache_index(self):
        """Тест работы cache'a index."""
        page = reverse('posts:index')
        Post.objects.create(
            text='Test text',
            author=self.user,
        )
        response = self.guest_client.get(page).content
        Post.objects.all().delete()
        response_1 = self.guest_client.get(page).content
        self.assertEqual(response, response_1)

    def test_cache_clear_index(self):
        """Тест работы очистки cache'a"""
        page = reverse('posts:index')
        Post.objects.create(
            text='Test text',
            author=self.user,
        )
        response = self.guest_client.get(page).content
        cache.clear()
        response_1 = self.guest_client.get(page).content
        self.assertNotEqual(response, response_1)


class FollowerTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.follower = User.objects.create_user(username='follower')
        cls.not_follower = User.objects.create_user(username='notafollower')

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.follower)

    def test_follow(self):
        """Авторизованный пользователь может подписываться"""
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author},
            )
        )
        follow = Follow.objects.filter(
            user=self.follower,
            author=self.author,
        ).exists()
        self.assertTrue(follow)

    def test_unfollow(self):
        """Авторизованный пользователь может отписываться"""
        Follow.objects.create(
            user=self.follower,
            author=self.author,
        )
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author},
            )
        )
        unfollow = Follow.objects.filter(
            user=self.follower,
            author=self.author,
        )
        self.assertFalse(unfollow)

    def test_follower_post_author_display(self):
        """Пользователь видит свои подписки"""
        test_text = 'Test text follow'
        Post.objects.create(
            author=self.author,
            text=test_text
        )
        Follow.objects.create(
            user=self.follower,
            author=self.author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        follow_post = response.context['page_obj'][FIRST_NUMBER]
        self.assertEqual(follow_post.text, test_text)
        self.assertEqual(follow_post.author, self.author)

    def test_not_follower_post_author_display(self):
        """Пользователь не видит чужие подписки"""
        test_text = 'Test text follow'
        Post.objects.create(
            author=self.author,
            text=test_text
        )
        Follow.objects.create(
            user=self.not_follower,
            author=self.author,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        ).context['page_obj']
        self.assertEqual(len(response), 0)
