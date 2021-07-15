from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_image_file_extension
from django_registration.forms import RegistrationForm
from django.utils.translation import gettext, gettext_lazy as _
from main.models import Voting


class InputForm(forms.Form):
    var = forms.CharField(
        min_length=1,
        max_length=100,
        required=True,
        label='Описание варианта',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Описание варианта',
                'class': 'form-control'
            }
        )
    )


class VotingContext(forms.Form):
    name = forms.CharField(
        min_length=1,
        max_length=100,
        required=True,
        label='Название голосования',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Название голосования',
                'class': 'form-control',
            }
        )
    )
    start_time = forms.DateTimeField(
        required=True,
        label='Начало голосования',
        widget=forms.DateTimeInput(
            attrs={
                'placeholder': 'Начало голосования',
                'class': 'form-control',
                'type': 'datetime-local'
            }
        )
    )
    finish_time = forms.DateTimeField(
        required=True,
        label='Окончание голосования',
        widget=forms.DateTimeInput(
            attrs={
                'placeholder': 'Окончание голосования',
                'class': 'form-control',
                'type': 'datetime-local'
            }
        )
    )
    image = forms.ImageField(
        required=False,
        label='Загрузите изображение',
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )
    desc = forms.CharField(
        min_length=1,
        max_length=200,
        required=True,
        label='Описание голосования',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Описание голосования',
                'class': 'form-control',
            }
        )
    )


class VoteForm(forms.Form):
    def __init__(self, voting_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        voting = Voting.objects.get(id=voting_id)
        self.fields['choices'].required = True
        self.fields['choices'].queryset = voting.votevariant_set.all()
        self.fields['choices'].label = ''


class VoteOneOfTwoForm(VoteForm):
    choices = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect(
            attrs={
                'class': 'btn-check',
            },
        ),
    )


class VoteOneOfManyForm(VoteForm):
    choices = forms.ModelChoiceField(
        queryset=None,
        widget=forms.RadioSelect,
    )


class VoteManyOfManyForm(VoteForm):
    choices = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
    )


class VotingEditForm(forms.Form):
    startdate = forms.DateTimeField(

        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'placeholder': 'Начало голосования',
                'class': 'form-control',
                'type': 'datetime-local'
            }
        )
    )
    enddate = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'placeholder': 'Начало голосования',
                'class': 'form-control',
                'type': 'datetime-local'
            }
        )
    )
    name = forms.CharField(
        min_length=1,
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'form': 'MainForm',
            }
        )
    )
    description = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'form': 'MainForm',
            }
        )
    )


class ProfileEditForm(forms.Form):
    name = forms.CharField(
        min_length=1,
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'form': 'MainForm',
            },
        ),
    )
    email = forms.EmailField(
        min_length=1,
        max_length=200,
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'form': 'MainForm',
            },
        ),
    )
    OldPass = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'form': 'MainForm',
            },
        ),
    )
    NewPass = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'form': 'MainForm',
            },
        ),
    )
    RepNewPass = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'form': 'MainForm',
            },
        ),
    )
    profile_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control form-control-sm',
                'form': 'MainForm',
            },
        ),
        validators=[
            validate_image_file_extension
        ],
    )


class ComplaintCreateForm(forms.Form):
    description = forms.CharField(
        required=True,
        label='',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Опишите вашу жалобу',
                'class': 'form-control',
                'style': 'width: 100%'
            }
        )
    )


class CustomRegistrationForm(RegistrationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'class': 'form-control'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta(UserCreationForm.Meta):
        fields = [
            User.USERNAME_FIELD,
            User.get_email_field_name(),
            "password1",
            "password2",
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class VotingSearchForm(forms.Form):
    voting_id = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': "form-control",
            'placeholder': "Введите номер голосования",
            'style': "height: 7vh; font-size: 1.2rem;",
            'required': 'true'
        }),
        label=''
    )
