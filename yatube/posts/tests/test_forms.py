import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, Comment

User = get_user_model()
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
UPLOADED_1 = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)
UPLOADED_2 = SimpleUploadedFile(
    name='test_image_2.gif',
    content=SMALL_GIF,
    content_type='image/test',
)
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPostCreateForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Test title',
            slug='test_slug',
            description='Test description',
        )
        cls.group_2 = Group.objects.create(
            title='Test title 2',
            slug='Test_slug_2',
            description='Test description 2',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Проверка создания поста"""
        posts_count = Post.objects.count()
        create_text = 'Test text create'
        form_data = {
            'text': create_text,
            'group': self.group.id,
            'image': UPLOADED_1,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.user},
            ),
        )
        last_posts = Post.objects.order_by('pub_date').last()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_posts.text, create_text)
        self.assertEqual(last_posts.group, self.group)
        self.assertEqual(last_posts.author, self.post.author)
        self.assertEqual(last_posts.image, f'posts/{UPLOADED_1.name}')

    def test_post_edit(self):
        """Проверка редактирование поста"""
        edit_text = 'Test new text'
        form_data = {
            'text': edit_text,
            'group': self.group_2.id,
            'image': UPLOADED_2,
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            ),
        )
        editing_post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(editing_post.text, edit_text)
        self.assertEqual(editing_post.group, self.group_2)
        self.assertEqual(editing_post.author, self.post.author)
        self.assertEqual(editing_post.image, f'posts/{UPLOADED_2.name}')

    def test_anonymous_comment(self):
        """
        Комментировать может только авторизованый пользователь.
        После коммента вернет на страницу поста.
        """
        comment_count = Comment.objects.count()
        comment_text = 'Test comment'
        form_data = {
            'text': comment_text
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk},
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            ),
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
