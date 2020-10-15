from django.contrib import admin
from .models import Essay, External, Page, PageRevision


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):

    fields = ('wiki', 'archived')


@admin.register(PageRevision)
class PageRevisionAdmin(admin.ModelAdmin):

    fields = ('page', 'title', 'content', 'edit_summary')


@admin.register(Essay)
class EssayAdmin(admin.ModelAdmin):

    fields = ('page', 'title', 'content', 'archived')


admin.site.register(External)
