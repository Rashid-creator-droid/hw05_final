from django.contrib import admin

from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    search_fields = (
        'text',
    )
    list_filter = (
        'pub_date',
    )
    list_editable = (
        'group',
    )
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
    )
    search_fields = (
        'title',
        'slug',
    )
    list_filter = (
        'title',
    )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
    )


admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)