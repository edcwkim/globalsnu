from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.views import generic
from project.utils import isascii
from haystack.query import SearchQuerySet
from itertools import chain
from .forms import SchoolAutodataUpdateForm
from .models import Country, School, SNUInWorld, Tag, TagLog, Like, Rating


class SNUInWorldList(LoginRequiredMixin, generic.TemplateView):

    template_name = "univ/snu_in_world_list.html"


class SNUInWorldDetail(LoginRequiredMixin, generic.DetailView):

    template_name = "univ/snu_in_world_detail.html"

    def get_object(self):
        return get_object_or_404(SNUInWorld, city=self.args[0])

    def get(self, *args, **kwargs):
        obj = self.get_object()
        if obj.redirect and obj.page:
            return redirect(obj.page)
        else:
            return super().get(*args, **kwargs)


class TagDetail(LoginRequiredMixin, generic.DetailView):

    model = Tag
    context_object_name = 'tag'
    template_name = "univ/tag_detail.html"


class SchoolList(LoginRequiredMixin, generic.ListView):

    context_object_name = 'schools'
    template_name = "univ/school_list.html"

    def get_queryset(self):
        return School.objects.filter(page__archived=False).order_by('-page__current_revision__edited')


class SchoolUpdate(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        school = get_object_or_404(School, pk=request.POST.get('pk'))
        if args[0] == 'country':
            country = get_object_or_404(Country, pk=request.POST.get('country_pk'))
            school.country = country
        elif args[0] == 'type':
            school.schltype = request.POST.get('school_type')
            pass
        elif args[0] == 'website':
            school.website = request.POST.get('website')
        school.save()
        return redirect(school)


class SchoolAutodataUpdate(LoginRequiredMixin, generic.UpdateView):

    model = School
    form_class = SchoolAutodataUpdateForm
    template_name = "univ/school_autodata_update.html"

    def form_valid(self, form):
        super().form_valid(form)
        self.object.update_coordinates()
        return redirect(self.object)


class SchoolTag(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            data = {}
            school = get_object_or_404(School, pk=request.POST.get('pk'))
            tag = Tag.objects.get_or_create(name=request.POST.get('tag_name'))[0]
            action = request.POST.get('action', '')
            if action == 'add':
                school.tags.add(tag)
                TagLog.objects.create(school=school, user=request.user, tag=tag,
                    is_addition=True)
            elif action == 'remove':
                school.tags.remove(tag)
                TagLog.objects.create(school=school, user=request.user, tag=tag,
                    is_addition=False)
            return JsonResponse(data)


class SchoolLike(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            data = {}
            school = get_object_or_404(School, pk=request.POST.get('pk'))
            try:
                like = Like.objects.get(school=school, user=request.user)
                like.delete()
            except ObjectDoesNotExist:
                Like.objects.create(school=school, user=request.user)
            return JsonResponse(data)


class SchoolRate(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            data = {}
            school = get_object_or_404(School, pk=request.POST.get('pk'))
            rate = int(request.POST.get('rate'))
            if rate in range(6):
                rating = Rating.objects.update_or_create(school=school,
                    user=request.user, defaults={'rate': rate})[0]
                data['average_rate'] = school.get_average_rating()
                if rating.rate == 0:
                    rating.delete()
            return JsonResponse(data)


class SchoolSearch(LoginRequiredMixin, generic.ListView):

    context_object_name = 'results'
    template_name = "univ/school_search.html"
    paginate_by = 20
    paginate_orphans = 1

    query = ''
    continent = []
    country = []
    language = []
    major = []

    def get_queryset(self):
        sqs = SearchQuerySet().models(School).exclude(page=None)

        def get_list(string):
            entries = string.split(',')
            for i, entry in enumerate(entries):
                if entry == '':
                    del entries[i]
                elif entry.isdigit():
                    entries[i] = int(entry)
            return entries

        self.query = self.request.GET.get('q', '')
        self.continent = get_list(self.request.GET.get('continent', ''))
        self.country = get_list(self.request.GET.get('country', ''))
        self.language = get_list(self.request.GET.get('language', ''))
        self.major = get_list(self.request.GET.get('major', ''))

        if self.query:
            if isascii(self.query):
                sqs = sqs.auto_query(self.query)
            else:
                sqs = sqs.autocomplete(text_auto=self.query)

        if self.continent:
            sqs = sqs.filter(continent__in=self.continent)
        if self.country:
            sqs = sqs.filter(country__in=self.country)
        if self.language:
            sqs = sqs.filter(tags__in=self.language)
        if self.major:
            sqs_inverse = sqs.exclude(tags__in=self.major)[:15]
            sqs = sqs.filter(tags__in=self.major)
            if not self.request.GET.get('strict', '') and sqs.count() < 3 and sqs_inverse:
                sqs = tuple(chain(sqs, sqs_inverse))
        return sqs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.query:
            context['query'] = self.query
            context['query_for_url'] = self.query.replace(' ', '_')
            query_for_matching = self.query.replace('_', ' ')
        else:
            query_for_matching = None
        context['no_matching_page'] = not School.objects.filter(
            page__current_revision__title__iexact=query_for_matching).exists()
        return context


class SchoolFilterSearch(LoginRequiredMixin, generic.RedirectView):

    def post(self, request, *args, **kwargs):
        query = '?'
        amp = ''
        if request.POST.get('continent', False):
            query += "continent={}".format(
                ','.join(request.POST.getlist('continent'))
            )
            amp = '&'
        if request.POST.get('country', False):
            query += "{}country={}".format(
                amp, ','.join(request.POST.getlist('country'))
            )
            amp = '&'
        if request.POST.get('language', False):
            query += "{}language={}".format(
                amp, ','.join(request.POST.getlist('language'))
            )
            amp = '&'
        if request.POST.get('major', False):
            query += "{}major={}".format(
                amp, ','.join(request.POST.getlist('major'))
            )

        return redirect(resolve_url('univ:school_search') + query)
