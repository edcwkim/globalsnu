from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UsernameField
from django.utils.translation import ugettext_lazy as _
from .models import User


class UserCreationForm(forms.ModelForm):

    field_order = ['email', 'nickname', 'password']

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
        # help_text=_("It is highly recommended that you use a different password from your original email."),
    )

    class Meta:
        model = User
        fields = ('email', 'nickname')
        field_classes = {'nickname': UsernameField}

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith("@snu.ac.kr"):
            raise forms.ValidationError(
                _("Email is not a valid mySNU email."),
                code='invalid',
            )
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        self.instance.email = self.cleaned_data.get('email')
        password_validation.validate_password(password, self.instance)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"/password/reset/\">this form</a>."
        ),
    )
    """
    major_id = forms.IntegerField(min_value=1, required=False,
        widget=forms.HiddenInput)
    """

    class Meta:
        model = User
        fields = ['nickname', 'password']
        field_classes = {'nickname': UsernameField}

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']

    """
    def clean_major_id(self):
        data = self.cleaned_data.get("major_id", None)
        if data:
            try:
                Major.objects.get(id=data)
            except:
                raise forms.ValidationError(
                    _("Invalid major."),
                    code='invalid',
                )
        return data
    """


class NicknameChangeForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['nickname']
        field_classes = {'nickname': UsernameField}
