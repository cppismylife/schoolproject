from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from django_registration.forms import RegistrationForm
from django.utils.translation import gettext_lazy as _
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
                'type': 'datetime-local',
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


# class VotingEditForm(forms.Form):
#     startdate = forms.DateTimeField(
#
#         required=False,
#         widget=forms.DateTimeInput(
#             attrs={
#                 'placeholder': 'Начало голосования',
#                 'class': 'form-control',
#                 'type': 'datetime-local'
#             }
#         )
#     )
#     enddate = forms.DateTimeField(
#         required=False,
#         widget=forms.DateTimeInput(
#             attrs={
#                 'placeholder': 'Начало голосования',
#                 'class': 'form-control',
#                 'type': 'datetime-local'
#             }
#         )
#     )
#     name = forms.CharField(
#         min_length=1,
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control',
#                 'form': 'MainForm',
#             }
#         )
#     )
#     description = forms.CharField(
#         required=False,
#         widget=forms.TextInput(
#             attrs={
#                 'class': 'form-control',
#                 'form': 'MainForm',
#             }
#         )
#     )


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


class VotingEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['next_voting'].queryset = user.voting_set.all().exclude(id=self.instance.id)
        self.fields['prev_voting'].queryset = user.voting_set.all().exclude(id=self.instance.id)
        self.fields['next_voting'].error_messages.update({
            'unique': f'Опрос с таким же полем "Следующий опрос" уже существует'
        })
        self.fields['prev_voting'].error_messages.update({
            'unique': f'Опрос с таким же полем "Предыдущий опрос" уже существует'
        })

        self.fields['type'].choices = (
            (0, 'Несколько ответов из нескольких вариантов'),
            (1, 'Один ответ из нескольких вариантов'),
            (2, 'Один ответ из двух вариантов')
        )

    def clean(self):
        cleaned_data = super().clean()
        next_voting = cleaned_data.get('next_voting')
        prev_voting = cleaned_data.get('prev_voting')
        finishes = cleaned_data.get('finishes')
        self.fields['image'].upload_to = 'votings'
        self.update_error_messages(next_voting, prev_voting)
        self.check_errors(finishes, next_voting, prev_voting)

    def update_error_messages(self, next_voting, prev_voting):
        self.next_voting_unique(next_voting)
        self.prev_voting_unique(prev_voting)

    def next_voting_unique(self, next_voting):
        if next_voting is not None:
            try:
                unique_voting = Voting.objects.get(next_voting=next_voting)
                self.fields['next_voting'].error_messages.update({
                    'unique': f'Опрос с таким же полем "Следующий опрос" уже существует('
                              f'{unique_voting})'
                })
            except Voting.DoesNotExist:
                pass

    def prev_voting_unique(self, prev_voting):
        if prev_voting is not None:
            try:
                unique_voting = Voting.objects.get(prev_voting=prev_voting)
                self.fields['prev_voting'].error_messages.update({
                    'unique': f'Опрос с таким же полем "Предыдущий опрос" уже существует('
                              f'{unique_voting})'
                })
            except Voting.DoesNotExist:
                pass

    def check_errors(self, finishes, next_voting, prev_voting):
        if next_voting is not None and prev_voting is not None:
            if next_voting == prev_voting:
                raise ValidationError('Следующий и предыдущий опросы не могут быть одинаковыми')
        if finishes is None:
            raise ValidationError('Укажите корректное время окончания опроса')
        if finishes <= self.instance.published:
            raise ValidationError(f'Окончание опроса долно быть не раньше его начала('
                                  f'{self.instance.published.strftime("%Y-%m-%d %H:%M")}) и текущего времени')

    class Meta:
        model = Voting
        exclude = ['author', 'published']
        widgets = {
            'description': forms.Textarea(attrs={'class': "form-control", 'rows': "5"}),
            'finishes': forms.DateTimeInput(attrs={
                'placeholder': 'Окончание голосования',
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'})
        },
        labels = {
            'name': 'Название',
            'description': 'Описание',
            'type': 'Тип',
            'finishes': 'Время окончания',
            'image': 'Изображение',
            'next_voting': 'Следующий опрос',
            'prev_voting': 'Предыдущий опрос'
        }
