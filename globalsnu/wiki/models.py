from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator, _lazy_re_compile
from django.db import models
from django.db.models import Max
from django.urls import NoReverseMatch, resolve, reverse
from django.utils.translation import get_language_info, ugettext_lazy as _
from globalsnu.utils import get_available_languages


class Wiki(models.Model):

    lang = models.CharField(
        _('language code'),
        max_length=5,
        unique=True,
        choices=get_available_languages(),
    )

    def __str__(self):
        language_name_english = get_language_info(self.lang)['name']
        return "{} Wiki".format(language_name_english)

    def get_language_name(self):
        return get_language_info(self.lang)['name_translated']

    def get_language_name_local(self):
        return get_language_info(self.lang)['name_local']


class Page(models.Model):

    wiki = models.ForeignKey(
        Wiki,
        models.PROTECT,
        related_name='pages',
        verbose_name=_('wiki'),
        default=1,
    )
    subid = models.PositiveIntegerField(
        _('sub id'),
        null=True,
    )
    current_revision = models.OneToOneField(
        'PageRevision',
        models.PROTECT,
        related_name='+',
        verbose_name=_('current revision'),
        blank=True,
        null=True,
    )
    title_for_url = models.CharField(
        _('title for URL'),
        max_length=150,
    )
    archived = models.BooleanField(
        _('archived'),
        default=False,
    )

    class Meta:
        unique_together = index_together = [
            ('wiki', 'subid'),
            ('wiki', 'title_for_url'),
        ]

    def __str__(self):
        return self.title or "Page {}".format(self.pk)

    @property
    def title(self):
        return getattr(self.current_revision, 'title', '')

    @property
    def content(self):
        return getattr(self.current_revision, 'content', '')

    @property
    def editor(self):
        return getattr(self.current_revision, 'editor', None)

    @property
    def editor_name(self):
        return getattr(self.current_revision, 'editor_name', '')

    @property
    def edited(self):
        return getattr(self.current_revision, 'edited', None)

    @property
    def creator(self):
        try:
            first_revision = self.revisions.get(revision_number=1)
        except ObjectDoesNotExist:
            return None
        else:
            return first_revision.editor

    @property
    def creator_name(self):
        try:
            first_revision = self.revisions.get(revision_number=1)
        except ObjectDoesNotExist:
            return ''
        else:
            return first_revision.editor_name

    @property
    def created(self):
        try:
            first_revision = self.revisions.get(revision_number=1)
        except ObjectDoesNotExist:
            return None
        else:
            return first_revision.edited

    @property
    def is_school(self):
        return hasattr(self, 'school')

    @property
    def is_country(self):
        return hasattr(self, 'country')

    def get_absolute_url(self):
        return reverse('wiki:page_detail', kwargs={'title': self.title_for_url})

    def revert_to_revision(self, revision):
        # TODO: move this to view
        if revision == self.current_revision:
            return None
        else:
            revision.pk = None
            revision.edit_summary = (
                _("Reverted to revision %s.") % revision.revision_number)
            return revision.save()

    def has_safe_title_for_url(self):
        # Check if there exists another page in the wiki with the same title_for_url
        collision = self.wiki.pages.filter(
            title_for_url=self.title_for_url,
        ).exclude(
            pk=self.pk,
        ).exists()
        if collision:
            return False

        # Check if this url resolves to another urlpattern with the same url
        try:
            url1 = self.get_absolute_url()
            res1 = resolve(url1)
            url2 = reverse(res1.view_name, args=res1.args, kwargs=res1.kwargs)
            return url1 == url2
        except NoReverseMatch:
            return True

    def save(self, *args, **kwargs):
        if not self.subid:
            aggregate = self.wiki.pages.aggregate(Max('subid'))
            self.subid = aggregate.get('subid__max', 0) + 1

        self.title_for_url = self.title.replace(' ', '_')
        while not self.has_safe_title_for_url():
            self.title_for_url += '_'
            if len(self.title_for_url) == 150:
                break
        return super().save(*args, **kwargs)


class PageRevision(models.Model):

    page = models.ForeignKey(
        Page,
        models.CASCADE,
        related_name='revisions',
        verbose_name=_('page'),
    )
    revision_number = models.PositiveSmallIntegerField(
        _('revision_number'),
        editable=False,
    )
    previous_revision = models.OneToOneField(
        'self',
        models.PROTECT,
        related_name='next_revision',
        verbose_name=_('previous revision'),
        blank=True,
        null=True,
    )

    title = models.CharField(
        _('title'),
        max_length=100,
        validators=[RegexValidator(
            _lazy_re_compile(r'^[^_/]+\Z'),
            _("The title cannot contain '_' or '/'."),
        )],
    )
    content = models.TextField(
        _('content'),
        max_length=65535,
        blank=True,
    )

    editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        related_name='edited_revisions',
        verbose_name=_('editor'),
        blank=True,
        null=True,
    )
    editor_name = models.CharField(
        _('editor name'),
        max_length=30,
        blank=True,
    )
    editor_email = models.EmailField(
        _('editor email'),
        blank=True,
    )
    edited = models.DateTimeField(
        _('edited time'),
        auto_now_add=True,
    )
    edit_summary = models.CharField(
        _('edit summary'),
        max_length=255,
    )

    class Meta:
        get_latest_by = 'edited'
        unique_together = index_together = ('page', 'revision_number')

    def __str__(self):
        return str(self.page) + " [{}]".format(self.revision_number)

    def get_absolute_url(self):
        return reverse('wiki:page_revision_detail', kwargs={
            'title': self.page.title_for_url,
            'revision_number': self.revision_number,
        })

    def save(self, *args, **kwargs):
        if self.editor:
            if not self.editor_name:
                self.editor_name = self.editor.get_full_name()
            if not self.editor_email:
                self.editor_email = self.editor.email

        if not self.id:
            page = self.page
            self.previous_revision = page.current_revision
            previous_number = getattr(self.previous_revision, 'revision_number', 0)
            self.revision_number = previous_number + 1
            super().save(*args, **kwargs)
            page.current_revision = self
            page.save(update_fields=['current_revision'])
            return self
        else:
            return super().save(*args, **kwargs)


class Essay(models.Model):
    """
    Privately owned posts that are attached to wiki pages.
    """
    page = models.ForeignKey(
        Page,
        models.SET_NULL,
        related_name='essays',
        verbose_name=_('page'),
        blank=True,
        null=True,
    )

    title = models.CharField(
        _('title'),
        max_length=100,
    )
    content = models.TextField(
        _('content'),
        max_length=1000000,
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        related_name='created_essays',
        verbose_name=_('creator'),
        blank=True,
        null=True,
    )
    creator_name = models.CharField(
        _('creator name'),
        max_length=30,
        blank=True,
    )
    creator_email = models.EmailField(
        _('creator email'),
        blank=True,
    )
    created = models.DateTimeField(
        _('created time'),
        auto_now_add=True,
    )
    edited = models.DateTimeField(
        _('edited time'),
        auto_now=True,
    )
    archived = models.BooleanField(
        _('archived'),
        default=False,
    )

    likers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_essays',
        verbose_name=_('users who liked'),
    )

    def __str__(self):
        return self.title or "Essay {}".format(self.pk)

    def get_absolute_url(self):
        return reverse('wiki:essay_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if self.creator:
            if not self.creator_name:
                self.creator_name = self.creator.get_full_name()
            if not self.creator_email:
                self.creator_email = self.creator.email
        return super().save(*args, **kwargs)


class External(models.Model):

    page = models.ForeignKey(
        Page,
        models.CASCADE,
        related_name='externals',
        verbose_name=_('page'),
    )

    SOURCES = [('WP', _('Wikipedia')), ('NW', _('Namu Wiki'))]
    source = models.CharField(
        _('source'),
        max_length=2,
        choices=SOURCES,
    )
    url = models.URLField(
        _('URL'),
    )

    ccl = models.BooleanField(
        _('CCL compatible'),
        default=False,
    )
    preview = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return "External {} from {}".format(self.pk, self.source)
