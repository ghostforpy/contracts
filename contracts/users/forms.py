from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.utils.translation import gettext_lazy as _
from django import forms

from .models import User, Contract, Company


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class ArhiveContarctFilterForm(forms.ModelForm):
    # query = forms.CharField(
    #     label="Поиск по ключевым словам", max_length=100, required=False
    # )
    number = forms.IntegerField(label="Номер контракта", required=False)
    object = forms.CharField(label="Наименование объекта", required=False)
    start = forms.DateField(label="Дата начала", required=False)
    end = forms.DateField(label="Дата окончания", required=False)
    description = forms.CharField(label="Описание работ", required=False)

    class Meta:
        model = Contract
        fields = [
            "number",
            "object",
            "start",
            "end",
            "company",
            "town",
            "description",
            "gip",
        ]


class ContarctFilterForm(ArhiveContarctFilterForm):
    class Meta:
        model = Contract
        fields = [
            "number",
            "object",
            "state",
            "start",
            "end",
            "company",
            "town",
            "description",
            "gip",
        ]
