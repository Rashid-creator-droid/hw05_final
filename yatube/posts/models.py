from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
FIRST_LETTER = 15


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='Ссылка',
    )
    description = models.TextField(
        max_length=500,
        verbose_name='Описание',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Все группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        max_length=2000,
        verbose_name='Текст',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Название группы',
        help_text='Введите описание группы',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = (
            '-pub_date',
        )
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        max_length=500,
        verbose_name="Текст комментария"
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка',
        verbose_name_plural = 'Подписки'
