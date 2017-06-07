import datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core import signing
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from globalsnu.core.mail import send_template_mail
from globalsnu.core.mixins import AjaxableResponseMixin
from globalsnu.univ.models import Like, School
from .forms import NicknameChangeForm, UserCreationForm
from .models import User


class Login(LoginView):

    extra_context = {'register_form': UserCreationForm()}


class Register(AjaxableResponseMixin, generic.CreateView):

    model = User
    form_class = UserCreationForm
    template_name = "registration/register.html"

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        Temporarily assign to dummy email "base@YYYY-MM-DD.HH-MM-SS.mmmmmm".
        Uses time information to prevent duplication.
        """
        email = form.instance.email
        base = email.rsplit('@')[0]
        domain = timezone.now().strftime('%Y-%m-%d.%H-%M-%S.%f')
        form.instance.email = "{}@{}".format(base, domain)
        form.instance.is_active = False
        self.object = form.save()
        self.send_verification_mail(email)
        return redirect('register_verify')

    def send_verification_mail(self, to):
        sign = signing.dumps(self.object.email, salt=settings.VERIFICATION_SALT)
        link = self.request.build_absolute_uri(resolve_url('verify', sign=sign))
        context = {
            'user': self.object,
            'link': link,
        }
        send_template_mail("mail/verify.html", context, to)

    def get_context_data(self, **kwargs):
        kwargs.setdefault('login_form', AuthenticationForm())
        return super().get_context_data(**kwargs)


class Verify(generic.RedirectView):

    pattern_name = settings.LOGIN_URL

    def get(self, request, *args, **kwargs):
        sign = kwargs['sign']
        try:
            email = signing.loads(sign, salt=settings.VERIFICATION_SALT,
                max_age=datetime.timedelta(weeks=1))
        except signing.BadSignature:
            messages.error(request, _("인증 실패: Bad Signature"))
        except signing.SignatureExpired:
            messages.error(request, _("인증 실패: Signature Expired"))
        else:
            messages.success(request, _("인증되었습니다."))
            user = get_object_or_404(User, email=email)
            user.email = email.rsplit('@')[0] + "@snu.ac.kr"
            user.is_active = True
            user.save()
        finally:
            return super().get(request, *args, **kwargs)


class Favorites(LoginRequiredMixin, generic.DetailView):

    context_object_name = 'user'
    template_name = "auth/favorites.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        # TODO: Favorites should cover liked essays for non-school pages

        user = self.object
        schools = School.objects.filter(
            Q(likers__in=[user]) |
            Q(page__essays__likers__in=[user])
        ).distinct()

        def get_liked_time(school):
            try:
                return Like.objects.get(school=school, user=user).time
            except ObjectDoesNotExist:
                return timezone.make_aware(
                    # prevent underflow
                    datetime.datetime.min + datetime.timedelta(days=1)
                )
        schools = sorted(schools, key=get_liked_time, reverse=True)

        schools_and_essays = []
        for school in schools:
            essays = user.liked_essays.filter(page__school=school)
            schools_and_essays.append((school, essays))
        kwargs.setdefault('schools_and_essays', schools_and_essays)
        return super().get_context_data(**kwargs)


class PersonalEdits(LoginRequiredMixin, generic.DetailView):

    context_object_name = 'user'
    template_name = "auth/personal_edits.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        revisions = self.object.edited_revisions.order_by('-edited')[:20]
        essays = self.object.created_essays.order_by('-created')[:20]
        kwargs.setdefault('revisions', revisions)
        kwargs.setdefault('essays', essays)
        return super().get_context_data(**kwargs)


class Settings(LoginRequiredMixin, generic.FormView):

    form_class = PasswordChangeForm
    success_url = reverse_lazy('settings')
    template_name = "auth/settings.html"

    @method_decorator(sensitive_post_parameters())
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        major_id = form.cleaned_data['major_id']
        if major_id:
            form.instance.major = get_object_or_404(Major, id=major_id)
        """
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "비밀번호가 변경되었습니다.")
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs.setdefault('nickname_form', NicknameChangeForm())
        return super().get_context_data(**kwargs)


class NicknameChange(LoginRequiredMixin, generic.View):

    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and not user.changed_nickname:
            form = NicknameChangeForm(data=request.POST)
            if form.is_valid():
                user.nickname = form.cleaned_data.get('nickname')
                user.changed_nickname = True
                user.save()
                messages.success(request, _("닉네임이 변경되었습니다."))
            else:
                for error in form.errors.get('nickname', []):
                    messages.error(request, error)
        return redirect('settings')


class Deactivate(LoginRequiredMixin, generic.View):

    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.check_password(request.POST.get('password')):
            user.is_active = False
            user.save(update_fields=['is_active'])
            return redirect('logout')
        else:
            messages.error(request, _("비밀번호가 일치하지 않습니다."))
            return redirect('settings')
