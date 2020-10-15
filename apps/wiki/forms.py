from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import Page, PageRevision, Essay


class PageCreateForm(forms.ModelForm):

    is_school = forms.BooleanField(label=_("학교 문서입니다."), required=False)
    is_country = forms.BooleanField(label=_("국가 문서입니다."), required=False)

    class Meta:
        model = PageRevision
        fields = ['title', 'content']

    def clean_title(self):
        data = self.cleaned_data['title']
        if Page.objects.filter(current_revision__title=data).exists():
            raise forms.ValidationError(
                _("Page with the title already exists."),
                code="exists",
            )
        return data


class PageUpdateForm(forms.ModelForm):

    is_school = forms.BooleanField(label=_("학교 문서입니다."), required=False)
    is_country = forms.BooleanField(label=_("국가 문서입니다."), required=False)

    class Meta:
        model = PageRevision
        fields = ['content', 'edit_summary']


class PageTitleUpdateForm(forms.ModelForm):

    class Meta:
        model = PageRevision
        fields = ['title', 'edit_summary']

    def clean_title(self):
        data = self.cleaned_data['title']
        if Page.objects.filter(current_revision__title=data).exclude(
                pk=self.instance.page.pk).exists():
            raise forms.ValidationError(
                _("Page with the title already exists."),
                code="exists",
            )
        return data


class EssayForm(forms.ModelForm):

    page_pk = forms.IntegerField(min_value=1, widget=forms.HiddenInput)

    class Meta:
        model = Essay
        fields = ['title', 'content']
