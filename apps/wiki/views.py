import random
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from apps.core.views import SimpleUserInteractionView
from apps.univ.models import Country, School, Rating
from .forms import PageCreateForm, PageUpdateForm, PageTitleUpdateForm, EssayForm
from .models import Essay, Page, PageRevision, Wiki


def get_current_wiki():
    try:
        return Wiki.objects.get(lang=translation.get_language())
    except ObjectDoesNotExist:
        return get_object_or_404(Wiki, pk=1)


class BasePageGetterMixin:

    page = None

    def dispatch(self, *args, **kwargs):
        self.page = self.get_page(kwargs['title'])
        return super().dispatch(*args, **kwargs)

    def get_page(self, title):
        try:
            page = get_object_or_404(Page, title_for_url=title, archived=False)
            lang = page.wiki.lang
            translation.activate(lang)
            self.request.session[translation.LANGUAGE_SESSION_KEY] = lang
            return page
        except MultipleObjectsReturned:
            return get_object_or_404(Page, wiki=get_current_wiki(),
                title_for_url=title, archived=False)


class PageGetterMixin(LoginRequiredMixin, BasePageGetterMixin):

    pass


class PageDetail(PageGetterMixin, generic.DetailView):

    context_object_name = 'page'

    def get_object(self):
        return self.page

    def get_template_names(self):
        template_names = ["wiki/page_detail.html"]
        if self.object.is_country:
            template_names.insert(0, "wiki/page_detail_country.html")
        if self.object.is_school:
            template_names.insert(0, "wiki/page_detail_school.html")
        return template_names

    def get_context_data(self, **kwargs):
        if self.object.is_school:
            school = self.object.school
            user = self.request.user
            kwargs.setdefault('user_liked', user in school.likers.all())
            try:
                user_rating = Rating.objects.get(school=school, user=user).rate
            except ObjectDoesNotExist:
                user_rating = 0
            finally:
                kwargs.setdefault('user_rating', user_rating)
            continents = Country.get_continents_with_countries()
            kwargs.setdefault('continents_left', continents[:3])
            kwargs.setdefault('continents_right', continents[3:])
        return super().get_context_data(**kwargs)


class PageList(LoginRequiredMixin, generic.ListView):

    model = Page
    context_object_name = 'pages'
    template_name = "wiki/page_list.html"

    def get_queryset(self):
        return Page.objects.filter(archived=False).order_by(
            '-current_revision__edited')


class PageCreate(LoginRequiredMixin, generic.CreateView):

    form_class = PageCreateForm
    template_name = "wiki/page_create.html"

    def get_initial(self):
        initial = super().get_initial()
        title = self.request.GET.get('title', '').replace('_', ' ')
        ptype = self.request.GET.get('is')
        initial['title'] = title
        initial['is_school'] = (ptype == 'school')
        initial['is_country'] = (ptype == 'country')
        return initial

    def form_valid(self, form):
        page = Page.objects.create(wiki=get_current_wiki())
        revision = form.save(commit=False)
        revision.page = page
        revision.editor = self.request.user
        revision.edit_summary = _("Created.")
        revision.save()
        if form.cleaned_data['is_school']:
            school = School.objects.update_or_create(
                name_cached=revision.title,
                defaults={'page': page},
            )[0]
            school.initialize_logo()
            school.initialize_address()
        if form.cleaned_data['is_country']:
            Country.objects.update_or_create(
                name_cached=revision.title,
                defaults={'page': page},
            )
        return redirect(page)


class PageUpdate(PageGetterMixin, generic.UpdateView):

    form_class = PageUpdateForm
    template_name = "wiki/page_update.html"

    def get_object(self):
        return self.page.current_revision

    def get_initial(self):
        initial = super().get_initial()
        initial['edit_summary'] = ''
        initial['is_school'] = self.page.is_school
        initial['is_country'] = self.page.is_country
        return initial

    def form_valid(self, form):
        page = self.page
        title = page.title
        PageRevision.objects.create(
            page=page,
            title=title,
            content=form.cleaned_data['content'],
            editor=self.request.user,
            edit_summary=form.cleaned_data['edit_summary'],
        )
        if form.cleaned_data['is_school'] and not page.is_school:
            school = School.objects.update_or_create(
                name_cached=title,
                defaults={'page': page},
            )[0]
            school.initialize_logo()
            school.initialize_address()
        elif not form.cleaned_data['is_school'] and page.is_school:
            school = page.school
            school.page = None
            school.save()
        if form.cleaned_data['is_country'] and not page.is_country:
            Country.objects.update_or_create(
                name_cached=title,
                defaults={'page': page},
            )
        elif not form.cleaned_data['is_country'] and page.is_country:
            country = page.country
            country.page = None
            country.save()
        return redirect(page)


class PageTitleUpdate(PageGetterMixin, generic.UpdateView):

    form_class = PageTitleUpdateForm
    template_name = "wiki/page_title_update.html"
    initial = {'edit_summary': ''}

    def get_object(self):
        return self.page.current_revision

    def form_valid(self, form):
        page = self.page
        PageRevision.objects.create(
            page=page,
            title=form.cleaned_data['title'],
            content=page.content,
            editor=self.request.user,
            edit_summary=form.cleaned_data['edit_summary']
        )
        return redirect(page)


class PageRevisionDetail(PageGetterMixin, generic.DetailView):

    context_object_name = 'revision'
    template_name = "wiki/page_revision_detail.html"

    def get_object(self):
        return get_object_or_404(PageRevision, page=self.page,
            revision_number=self.kwargs['revision_number'])

    def get_context_data(self, **kwargs):
        previous_revision = self.object.previous_revision
        if previous_revision:
            kwargs.setdefault('prev', previous_revision)
            kwargs.setdefault('prev_prev', previous_revision.previous_revision)
        if hasattr(self.object, 'next_revision'):
            next_revision = self.object.next_revision
            kwargs.setdefault('next', next_revision)
            kwargs.setdefault('next_next',
                getattr(next_revision, 'next_revision', None))
        return super().get_context_data(**kwargs)


class PageHistory(PageGetterMixin, generic.ArchiveIndexView):

    context_object_name = 'revisions'
    template_name = "wiki/page_history.html"

    date_field = 'edited'
    paginate_by = 25
    paginate_orphans = 1

    def get(self, request, *args, **kwargs):
        self.queryset = self.page.revisions.all()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs.setdefault('page', self.page)
        return super().get_context_data(**kwargs)


class PageRandom(LoginRequiredMixin, generic.RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        wiki = get_current_wiki()
        queryset = wiki.pages.filter(archived=False)
        if queryset:
            index = random.randrange(len(queryset))
            return resolve_url(queryset[index])
        else:
            messages.error(self.request, _("No page exists."))
            return resolve_url('home')


class EssayDetail(LoginRequiredMixin, generic.DetailView):

    model = Essay
    context_object_name = 'essay'
    template_name = "wiki/essay_detail.html"

    def get_context_data(self, **kwargs):
        kwargs.setdefault('user_liked',
            self.request.user in self.object.likers.all())
        return super().get_context_data(**kwargs)


class EssayList(LoginRequiredMixin, generic.ListView):

    queryset = Essay.objects.filter(archived=False, page__archived=False)
    ordering = '-created'
    context_object_name = 'essays'
    template_name = "wiki/essay_list.html"


class EssayCreate(PageGetterMixin, generic.CreateView):

    form_class = EssayForm
    template_name = "wiki/essay_create.html"

    def get_initial(self):
        initial = super().get_initial()
        initial['page_pk'] = self.object.page.pk
        return initial

    def get_context_data(self, **kwargs):
        kwargs.setdefault('page', self.page)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        page_pk = form.cleaned_data['page_pk']
        form.instance.page = get_object_or_404(Page, pk=page_pk, archived=False)
        form.instance.creator = self.request.user
        return super().form_valid(form)


class EssayUpdate(UserPassesTestMixin, generic.UpdateView):

    model = Essay
    form_class = EssayForm
    template_name = "wiki/essay_update.html"

    def test_func(self):
        return lambda s: s.request.user == s.get_object().creator

    def get_initial(self):
        initial = super().get_initial()
        initial['page_pk'] = self.object.page.pk
        return initial


class EssayLike(SimpleUserInteractionView):

    model = Essay
    check_archived = True

    def interact(self, request):
        user = request.user
        likers_manager = self.object.likers
        if user in likers_manager.all():
            likers_manager.remove(user)
        else:
            likers_manager.add(user)
