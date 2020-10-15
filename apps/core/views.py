from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.views import generic
from apps.auth.views import Login
from apps.univ.models import Country, School, Tag
from apps.wiki.models import Essay
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet


class SimpleUserInteractionView(LoginRequiredMixin, generic.View):

    model = None
    object = None
    check_archived = False
    ajax_resp_data = {}

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            self.raise_exception = True
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.interact(request)
        if request.is_ajax():
            return JsonResponse(self.ajax_resp_data)
        else:
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer or self.object)

    def interact(self, request):
        raise ImproperlyConfigured()

    def get_object(self):
        kwarg = {'archived': False} if self.check_archived else {}
        return get_object_or_404(self.model, pk=self.request.POST.get('pk'),
            **kwarg)


class Home(generic.TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.template_name = "core/home.html"
            return super().dispatch(request, *args, **kwargs)
        else:
            return Login.as_view()(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['disable_ccl'] = True
        if self.request.user.is_authenticated:
            context['school_search'] = SearchForm()
            context['CONTINENTS'] = Country.CONTINENTS
            context['countries'] = Country.objects.order_by('page__current_revision__title').all()
            context['language_tags'] = Tag.objects.filter(category__name='언어').order_by('name').all()
            context['major_tags'] = Tag.objects.filter(category__name='전공').order_by('name').all()
            context['schools'] = School.objects.filter(page__archived=False).order_by('-page__current_revision__edited').all()[:6]
            context['essays'] = Essay.objects.filter(page__archived=False).order_by('-created').all()[:6]
        return context


class Manual(LoginRequiredMixin, generic.TemplateView):

    template_name = "core/manual.html"

    def get(self, request, *args, **kwargs):
        if request.user_agent.is_mobile:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(resolve_url('home') + "#manual")


class Manual2(LoginRequiredMixin, generic.TemplateView):

    template_name = "core/manual_2.html"

    def get(self, request, *args, **kwargs):
        if request.user_agent.is_mobile:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(resolve_url('home') + "#manual-2")


class Autocomplete(generic.View):

    def dispatch(self, request, *args, **kwargs):
        scope = kwargs.get('scope', '')
        query = request.GET.get('q', '')
        fetch_url = request.GET.get('fetch_url', False)

        if scope == 'tag':
            sqs = SearchQuerySet().models(Tag).autocomplete(name_auto=query)[:5]
            exists = Tag.objects.filter(name__iexact=query).exists()
        else:
            sqs = SearchQuerySet().autocomplete(name_auto=query)[:5]
            exists = False

        if fetch_url:
            data = {
                'results': [{
                    'name': result.object.name,
                    'url': resolve_url(result.object)
                } for result in sqs],
                'exists': exists,
            }
        else:
            data = {
                'results': [{
                    'name': result.object.name,
                } for result in sqs],
                'exists': exists,
            }
        return JsonResponse(data)
