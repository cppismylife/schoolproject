"""schoolproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse
from django_registration.backends.one_step.views import RegistrationView

from main import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# base
from main.forms import CustomRegistrationForm, CustomUserLoginForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index_page, name='index'),
]

# votings
urlpatterns += [
    path('votings_list/', views.votings_page, name='votings_list'),
    path('create_voting/', views.create_voting_page, name='create_voting'),
    path('voting/<int:id>/', views.VotingPage.as_view(), name='voting_page'),
    path('voting/<int:pk>/edit/', views.VotingEdit.as_view(), name='voting_edit'),
    path('voting/<int:id>/vote/', views.vote_page, name='vote'),
    path('voting/<int:id>/results/', views.VotingResults.as_view(), name='results_page'),
    path('voting_search/', views.VotingSearch.as_view(), name='voting_search'),
    path('voting/<int:pk>/delete', views.VotingDeleteView.as_view(), name='voting_delete')
]

# profile
urlpatterns += [
    path('profile_edit/', views.profile_edit_page, name='profile_edit'),
    path('profile/<int:id>/', views.profile_page, name='profile'),
]

# password_reset
urlpatterns += [
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/pas_res_form.html',
            extra_context={
                'menu': views.get_menu_context(),
                'pagename': 'Восстановление пароля'
            }
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/pas_res_done.html',
            extra_context={
                'menu': views.get_menu_context(),
                'pagename': 'Восстановление пароля'
            }
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/pas_res_confirm.html',
            extra_context={
                'menu': views.get_menu_context(),
                'pagename': 'Восстановление пароля'
            }
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/pas_res_complete.html',
            extra_context={
                'menu': views.get_menu_context(),
                'pagename': 'Восстановление пароля'
            }
        ),
        name='password_reset_complete'
    ),
]

# auth_and_register
urlpatterns += [
    path('accounts/register/',
         RegistrationView.as_view(
             form_class=CustomRegistrationForm,
             success_url=reverse('index')
         ), name='register'),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', auth_views.LoginView.as_view(
        extra_context={
            'menu': views.get_menu_context(),
            'pagename': 'Авторизация'
        },
        authentication_form=CustomUserLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Нужно для отображения изображения на странице
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
