import datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.generic import TemplateView, FormView, UpdateView, DeleteView
from plotly.subplots import make_subplots
from plotly.io import to_html
from main.extra_func import get_forms, check_valid_and_create, check_eligible_to_vote
from main.forms import InputForm, VotingContext, VoteOneOfTwoForm, \
    VoteOneOfManyForm, VoteManyOfManyForm, ProfileEditForm, VotingEditForm, VotingSearchForm
from main.models import Voting, VoteVariant, VoteFact, User
from django_registration.backends.one_step.views import RegistrationView


def get_menu_context(auth=False):
    pages = [
        {'url_name': 'voting_search', 'name': 'Найти опрос'}
    ]
    if auth:
        pages += [
            {'url_name': 'votings_list', 'name': 'Мои опросы'},
            {'url_name': 'create_voting', 'name': 'Создать опрос'},
        ]
    return pages


def index_page(request):
    context = {
        'pagename': 'Опросы и голосования',
        'pages': 4,
        'auth': request.user.is_authenticated,
        'menu': get_menu_context(request.user.is_authenticated)
    }
    return render(request, 'pages/index.html', context)


class TemplatePage(TemplateView):
    template_name = 'DEFINE ME'

    def get_context_data(self, **kwargs):
        return {
            'menu': get_menu_context(self.request.user.is_authenticated),
            'voting': get_object_or_404(Voting, id=kwargs['id']),
            'today': timezone.now()
        }


class VotingPage(TemplatePage):
    template_name = 'pages/voting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Просмотр опроса'
        context['eligible_to_vote'] = check_eligible_to_vote(
            Voting.objects.get(id=kwargs['id']), self.request
        )
        return context


class VotingResults(VotingPage):
    template_name = 'pages/voting_results.html'

    def get_context_data(self, **kwargs):
        facts = self.count_facts(**kwargs)
        context = super().get_context_data(**kwargs)
        context['facts'] = facts
        context['pagename'] = 'Результаты опроса'
        if len([value for value in facts.values() if value]):
            context['plotly'] = self.create_chart(facts.copy())
        return context

    @staticmethod
    def count_facts(**kwargs):
        variants = get_list_or_404(VoteVariant, voting=kwargs['id'])
        facts = {}
        for variant in variants:
            facts.update({
                variant.description: variant.votefact_set.count()
            })
        return facts

    @staticmethod
    def create_chart(facts: dict):
        zero_keys = [key for key, value in facts.items() if value == 0]
        [facts.pop(key) for key in zero_keys]
        fig = make_subplots(rows=1, cols=2, specs=[
            [{'type': 'xy'}, {'type': 'domain'}]
        ])
        fig.add_bar(
            row=1, col=1,
            x=list(facts.keys()),
            y=list(facts.values()),
            name='',
            showlegend=False,
            hovertemplate='Вариант: %{x}<br>Количество голосов: %{y}',
            marker_color=['grey'] * len(list(facts.items())),
            hoverlabel_font_color='white',
        )
        fig.add_pie(
            row=1, col=2,
            values=list(facts.values()),
            labels=list(facts.keys()),
            textposition="auto",
            name='',
            hovertemplate='Вариант: %{label}<br>Количество голосов: %{value}</br>%{percent}',
        )
        fig.update_layout(yaxis_tickformat=',d')
        fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
        fig.update_yaxes(row=1, col=1, title_text='Количество голосов')
        fig.update_xaxes(row=1, col=1, title_text='Варианты ответов')
        return to_html(fig, full_html=False, include_plotlyjs='cdn')


def vote_page(request, **kwargs):
    context = {
        'menu': get_menu_context(request.user.is_authenticated),
        'pagename': 'Голосование'
    }

    def get_vote_form_type(voting_type: int) -> callable:
        """
        function to decide form class for different Voting types
        :param voting_type:
        :return: VoteForm
        """
        if voting_type == Voting.CHECKBOXES:
            return VoteManyOfManyForm
        elif voting_type == Voting.RADIOS:
            return VoteOneOfManyForm
        elif voting_type == Voting.BUTTONS:
            return VoteOneOfTwoForm

    # get the Voting to work with
    voting: Voting = get_object_or_404(Voting, id=kwargs['id'])

    if not check_eligible_to_vote(voting, request):
        raise PermissionDenied('Can not vote on this voting')

    if request.method == 'POST':

        # determine form type and create form from POST request
        form_type = get_vote_form_type(voting.type)
        form = form_type(kwargs['id'], request.POST)

        if form.is_valid():
            data = form.cleaned_data
            vote_fact_user = None
            if request.user.is_authenticated:
                vote_fact_user = request.user
            vote_fact = VoteFact(
                created=timezone.now(),
                user=vote_fact_user,
            )
            # save new vote fact to use it's id in the ManyToMany relationship
            vote_fact.save()
            if form_type == VoteOneOfTwoForm or form_type == VoteOneOfManyForm:
                vote_fact.variants.add(data['choices'])
            elif form_type == VoteManyOfManyForm:
                vote_fact.variants.set(data['choices'])
            vote_fact.save()

            votes = request.session.get('votes')
            if votes:
                votes.append(voting.id)
                request.session.modified = True
            else:
                request.session['votes'] = [voting.id]

        # redirect user to results page after creating VoteFact
        return redirect('results_page', id=voting.id)

    else:
        context['voting'] = voting
        form = get_vote_form_type(voting.type)(voting_id=voting.id)
        context['form'] = form
        return render(request, 'pages/vote.html', context)


def votings_page(request):
    context = {
        'pagename': 'Список опросов',
        'menu': get_menu_context(request.user.is_authenticated),
    }
    user = request.user
    if user is not None:
        context['votings'] = Voting.objects.filter(author=user)
        context['today'] = timezone.now()
    return render(request, 'pages/votings_list.html', context)


@login_required()
def create_voting_page(request):
    context = {
        'pagename': 'Создать опрос',
        'menu': get_menu_context(request.user.is_authenticated),
        'type_of': request.POST.get('type_of', "1"),
        'nums': [0, 1, 2],
        'create': int(request.POST.get('create', 0)),
        'accordion_context': {
            '1': {'name': 'Опрос "Несколько ответов из нескольких вариантов"',
                  'number': 'One',
                  'count': max(int(request.POST.get('count1', 2)), 2),
                  'forms': list(),
                  },
            '2': {'name': 'Опрос "Один из ответ из нескольких вариантов"',
                  'number': 'Two',
                  'count': max(int(request.POST.get('count2', 2)), 2),
                  'forms': list(),
                  },
            '3': {'name': 'Опрос "Один ответ из двух вариантов"',
                  'number': 'Three',
                  'count': max(int(request.POST.get('count3', 2)), 2),
                  'forms': list(),
                  },
        }
    }
    flag = False
    if request.method == 'POST':
        voteinfo = VotingContext(request.POST, request.FILES)
        context['form'] = voteinfo
        forms = get_forms(context, request)
        if context['create']:
            flag = check_valid_and_create(context, forms, request, voteinfo)
    elif request.method == 'GET':
        context['form'] = VotingContext()
        for i in range(1, 3):
            for according_num in ['1', '2', '3']:
                context['accordion_context'][according_num]['forms'].append(InputForm(prefix=str(i) + according_num))
    if flag:
        return redirect('voting_page', id=context["v_id"])
    if context['create']:
        context['errors'] = list()
        for error in voteinfo.errors:
            if error == 'start_time':
                context['errors'].append('Неправильное время начала опроса')
            elif error == 'finish_time':
                context['errors'].append('Неправильное время окончания опроса')
        if voteinfo.is_valid():
            if timezone.now() >= parse_datetime(voteinfo.data['start_time']).astimezone() + datetime.timedelta(
                minutes=3):
                context['errors'].append('Начало опроса должно быть не раньше текущего времени')
            if parse_datetime(voteinfo.data['start_time']) >= parse_datetime(voteinfo.data['finish_time']):
                context['errors'].append('Окончание опроса должно быть позже начала')
    return render(request, 'pages/create_voting.html', context)


@login_required()
def profile_edit_page(request):
    context = {
        'pagename': 'Редактировать профиль',
        'menu': get_menu_context(request.user.is_authenticated),
        'CN': request.POST.get('ChangeName', False),
        'CE': request.POST.get('ChangeEmail', False),
        'CP': request.POST.get('ChangePassword', False),
        'Create': int(request.POST.get('Create', 0)),
        'errors': [],
    }

    form = ProfileEditForm(request.POST, request.FILES)
    context['form'] = form

    if request.method == "POST" and context['Create'] == 1:
        if form.is_valid():
            for changed_field in form.changed_data:
                if changed_field == 'name':
                    request.user.username = form.cleaned_data['name']

                elif changed_field == 'email':
                    request.user.email = form.cleaned_data['email']

                elif changed_field == 'NewPass':
                    if form.cleaned_data['NewPass'] == form.cleaned_data['RepNewPass']:
                        if request.user.check_password(form.cleaned_data['OldPass']):
                            try:
                                validate_password(form.cleaned_data['NewPass'])
                                request.user.set_password(form.cleaned_data['NewPass'])
                            except ValidationError as err:
                                context['errors'] += err
                        else:
                            context['errors'].append('Неверный старый пароль')
                    else:
                        context['errors'].append('Пароли не совпадают')

                elif changed_field == 'profile_image':
                    request.user.profile.profile_image = form.files['profile_image']

            if not context['errors']:
                try:
                    request.user.save()
                    return redirect('profile', request.user.id)
                except IntegrityError:
                    context['errors'].append('Имя пользователя уже занято')

        else:
            context['errors'] += form.errors.values()

    return render(request, 'pages/profile_edit.html', context)


@login_required()
def profile_page(request, id):
    if request.user.id != id and not request.user.is_superuser and not request.user.is_staff:
        raise PermissionDenied('Вы не можете просматривать профиль этого пользователя')
    context = {
        'menu': get_menu_context(request.user.is_authenticated),
        'pagename': 'Профиль'
    }
    user = get_object_or_404(User, id=id)
    votings = user.voting_set.all()
    votes = user.votefact_set.all()
    context['votings'] = votings
    context['votes'] = votes
    context['user'] = user
    user_votings = set()
    for votefact in votes:
        user_votings.add(votefact.variants.all()[0].voting)
    context['user_votings'] = list(user_votings)
    return render(request, 'pages/profile.html', context)


class VotingSearch(FormView):
    template_name = 'pages/voting_search.html'
    form_class = VotingSearchForm

    def form_valid(self, form):
        return redirect('voting_page', form.cleaned_data['voting_id'])

    def get_context_data(self, **kwargs):
        context = super(VotingSearch, self).get_context_data(**kwargs)
        context['pagename'] = 'Найти опрос'
        context['menu'] = get_menu_context(self.request.user.is_authenticated)
        return context


class VotingDeleteView(LoginRequiredMixin, DeleteView):
    model = Voting
    success_url = reverse_lazy('votings_list')

    def get_context_data(self, **kwargs):
        raise PermissionDenied


class VotingEdit(LoginRequiredMixin, UpdateView):
    template_name = 'pages/votingEdit.html'
    model = Voting
    form_class = VotingEditForm

    def get_form_kwargs(self):
        kwargs = super(VotingEdit, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('voting_page', kwargs={'id': self.object.id})

    def get_context_data(self, **kwargs):
        if self.request.user == get_object_or_404(Voting, id=self.kwargs['pk']).author or self.request.user.is_staff or self.request.user.is_superuser:
            context = super().get_context_data(**kwargs)
            context['pagename'] = 'Редактировать опрос'
            context['menu'] = get_menu_context(self.request.user.is_authenticated)
            context['id'] = self.kwargs['pk']
            return context
        else:
            raise PermissionDenied


class CustomRegistrationView(RegistrationView):
    def form_valid(self, form):
        super().form_valid(form)
        redirect_to = self.request.GET.get('next')
        if form.is_valid():
            return redirect(redirect_to if redirect_to else '/')


class CustomLogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        session_votes = request.session.get('votes')
        if request.user.is_authenticated:
            session_data = self.get_user_votes(request.user)
            if session_votes:
                session_data.update(session_votes)
        else:
            session_data = session_votes
        logout(request)
        self.request.session['votes'] = list(session_data)
        return redirect('index')

    @staticmethod
    def get_user_votes(user):
        votes = set()
        votefacts = VoteFact.objects.filter(user=user)
        for votefact in votefacts:
            votes.add(votefact.variants.all()[0].voting.id)
        return votes
