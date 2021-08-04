import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.generic import TemplateView, FormView, UpdateView
from plotly.graph_objs import Figure, Pie, Bar
from plotly.subplots import make_subplots
from plotly.io import to_html
from main.extra_func import get_forms, check_valid_and_create, check_eligible_to_vote
from main.forms import InputForm, VotingContext, VoteOneOfTwoForm, \
    VoteOneOfManyForm, VoteManyOfManyForm, ProfileEditForm, \
    ComplaintCreateForm, VotingEditForm, VotingSearchForm
from main.models import Voting, VoteVariant, VoteFact, Complaint, User


def get_menu_context(auth=False):
    if auth:
        return [
            {'url_name': 'votings_list', 'name': 'Голосования'},
            {'url_name': 'create_voting', 'name': 'Создать голосование'},
        ]
    else:
        return [
            {'url_name': 'votings_list', 'name': 'Голосования'}
        ]


@login_required()
def voting_edit(request, **kwargs):
    context = {
        'pagename': 'Редактировать голосование',
        'menu': get_menu_context(request.user.is_authenticated),
        'SV': request.POST.get('startdate', False),
        'EV': request.POST.get('enddate', False),
        'CN': request.POST.get('name', False),
        'CD': request.POST.get('description', False),
        'Create': int(request.POST.get('Create', 0)),

    }

    # get the Voting to work with
    voting = Voting.objects.get(id=kwargs['id'])
    vot = VotingEditForm(request.POST)
    context['form'] = vot
    if (voting.finishes < timezone.now()) or (voting.author != request.user):
        raise PermissionDenied('can not edit this voting')

    if request.method == 'POST':
        if context['SV'] == 'change':
            try:

                # vot.fields['startdate'].clean(value=vot.data['startdate'])
                voting.published = timezone.now()  # vot.data['startdate']
                voting.save()
            except:
                raise NotImplementedError
        if context['EV'] == 'change':
            try:

                # vot.fields['startdate'].clean(value=vot.data['startdate'])
                voting.finishes = timezone.now()  # vot.data['startdate']
                voting.save()
            except:
                raise NotImplementedError
        context['errors'] = list()
        if vot.is_valid():
            for changed_field in vot.changed_data:
                if changed_field == 'name':
                    voting.name = vot.cleaned_data['name']
                elif changed_field == "startdate":
                    if timezone.now() >= parse_datetime(
                        vot.changed_data['start_time']).astimezone() + datetime.timedelta(minutes=1):
                        context['errors'].append('Начало голосования должно быть не раньше текущего времени')
                    else:
                        voting.startdate = vot.cleaned_data["startdate"]
                elif changed_field == "enddate":
                    if parse_datetime(vot.changed_data['start_time']) >= parse_datetime(
                        vot.changed_data['finish_time']):
                        context['errors'].append('Окончание голосования должно быть позже начала')
                    else:
                        voting.startdate = vot.cleaned_date['startdate']
                elif changed_field == 'description':
                    voting.description = vot.cleaned_data['description']
            voting.save()

        for error in vot.changed_data:
            if error == 'start_time':
                context['errors'].append('Неправильное время начала голосования')
            elif error == 'finish_time':
                context['errors'].append('Неправильное время окончания голосования')

        return redirect('voting_page', **kwargs)

    else:
        context['voting'] = voting

        context['voting.id'] = voting.id

        context['votevariants'] = voting.votevariant_set.all()

    return render(request, 'pages/voting_edit.html', context)


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
        context['pagename'] = 'Просмотр голосования'
        context['eligible_to_vote'] = check_eligible_to_vote(
            Voting.objects.get(id=kwargs['id']), self.request.user
        )
        return context


class VotingResults(VotingPage):
    template_name = 'pages/voting_results.html'

    def get_context_data(self, **kwargs):
        facts = self.count_facts(**kwargs)
        context = super().get_context_data(**kwargs)
        context['facts'] = facts
        context['pagename'] = 'Результаты голосования'
        if len([value for value in facts.values() if value]):
            context['plotly'] = self.create_chart(facts)
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
        fig = make_subplots(rows=1, cols=2, specs=[
            [{'type': 'xy'}, {'type': 'domain'}]
        ])
        fig.add_bar(
            row=1, col=1,
            x=list(facts.keys()),
            y=list(facts.values()),
            name='',
            showlegend=False,
            y0=0
        )
        fig.add_pie(
            row=1, col=2,
            values=list(facts.values()),
            labels=list(facts.keys()),
            textposition="auto",
            name=''
        )

        return to_html(fig, full_html=False, include_plotlyjs='cdn')


class ComplaintCreate(LoginRequiredMixin, FormView):
    template_name = 'pages/complaint_create.html'
    form_class = ComplaintCreateForm
    success_url = ''

    def form_valid(self, form):
        context = self.get_context_data()
        context['success'] = True

        record = Complaint(
            voting=get_object_or_404(Voting, id=self.kwargs['id']),
            author=self.request.user,
            description=form.cleaned_data['description'].strip(),
            status=0,
            created=timezone.now()
        )
        record.save()
        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        return {
            'menu': get_menu_context(self.request.user.is_authenticated),
            'voting': get_object_or_404(Voting, id=self.kwargs['id']),
            'today': timezone.now(),
            'form': self.get_form_class(),
            'pagename': 'Пожаловаться'
        }


@login_required()
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

    if not check_eligible_to_vote(voting, request.user):
        raise PermissionDenied('can not vote on this voting')

    if request.method == 'POST':

        # determine form type and create form from POST request
        form_type = get_vote_form_type(voting.type)
        form = form_type(kwargs['id'], request.POST)

        if form.is_valid():
            data = form.cleaned_data

            vote_fact = VoteFact(
                created=timezone.now(),
                user=request.user,
            )
            # save new vote fact to use it's id in the ManyToMany relationship
            vote_fact.save()
            if form_type == VoteOneOfTwoForm or form_type == VoteOneOfManyForm:
                vote_fact.variants.add(data['choices'])
            elif form_type == VoteManyOfManyForm:
                vote_fact.variants.set(data['choices'])

            vote_fact.save()

        # redirect user to results page after creating VoteFact
        return redirect('results_page', id=voting.id)

    else:
        context['voting'] = voting
        form = get_vote_form_type(voting.type)(voting_id=voting.id)
        context['form'] = form
        return render(request, 'pages/vote.html', context)


def votings_page(request):
    context = {
        'pagename': 'Список голосований',
        'menu': get_menu_context(request.user.is_authenticated),
    }
    user_id = request.GET.get('user', None)
    if user_id is not None:
        context['votings'] = Voting.objects.filter(author=user_id)
    else:
        context['votings'] = Voting.objects.filter(
            published__lt=timezone.now(),
            finishes__gt=timezone.now(),
        )
    return render(request, 'pages/votings_list.html', context)


@login_required()
def create_voting_page(request):
    context = {
        'pagename': 'Создать голосование',
        'menu': get_menu_context(request.user.is_authenticated),
        'type_of': request.POST.get('type_of', "1"),
        'nums': [0, 1, 2],
        'create': int(request.POST.get('create', 0)),
        'accordion_context': {
            '1': {'name': 'Голосование "Несколько ответов из нескольких вариантов"',
                  'number': 'One',
                  'count': max(int(request.POST.get('count1', 2)), 2),
                  'forms': list(),
                  },
            '2': {'name': 'Голосование "Один из ответ из нескольких вариантов"',
                  'number': 'Two',
                  'count': max(int(request.POST.get('count2', 2)), 2),
                  'forms': list(),
                  },
            '3': {'name': 'Голосование "Один ответ из двух вариантов"',
                  'number': 'Three',
                  'count': max(int(request.POST.get('count3', 2)), 2),
                  'forms': list(),
                  },
        }
    }
    flag = False
    voteinfo = VotingContext(request.POST, request.FILES)
    context['voteinfo'] = voteinfo

    if request.method == 'POST':
        forms = get_forms(context, request)
        if context['create']:
            flag = check_valid_and_create(context, forms, request, voteinfo)
    elif request.method == 'GET':
        for i in range(1, 3):
            for according_num in ['1', '2', '3']:
                context['accordion_context'][according_num]['forms'].append(InputForm(prefix=str(i) + according_num))
    if flag:
        return redirect('voting_page', id=context["v_id"])
    if context['create']:
        context['errors'] = list()
        for error in voteinfo.errors:
            if error == 'start_time':
                context['errors'].append('Неправильное время начала голосования')
            elif error == 'finish_time':
                context['errors'].append('Неправильное время окончания голосования')
        if voteinfo.is_valid():
            if timezone.now() >= parse_datetime(voteinfo.data['start_time']).astimezone() + datetime.timedelta(
                minutes=3):
                context['errors'].append('Начало голосования должно быть не раньше текущего времени')
            if parse_datetime(voteinfo.data['start_time']) >= parse_datetime(voteinfo.data['finish_time']):
                context['errors'].append('Окончание голосования должно быть позже начала')
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
        raise PermissionDenied('can not view this profile')

    context = {
        'menu': get_menu_context(request.user.is_authenticated),
        'pagename': 'Профиль'
    }
    user = get_object_or_404(User, id=id)
    votings = user.voting_set.all()
    votes = user.votefact_set.all()
    complaints = user.complaint_set.all()

    if request.method == 'POST':
        if request.user.is_superuser:
            if request.POST.get('action', None) == 'set_moder':
                user.is_staff = True
                user.save()
            elif request.POST.get('action', None) == 'reset_moder':
                user.is_staff = False
                user.save()
        else:
            raise PermissionDenied
    context['votings'] = votings
    context['complaints'] = complaints
    context['votes'] = votes
    context['user'] = user
    return render(request, 'pages/profile.html', context)


@login_required()
def complaint_page(request, id):
    complaint = get_object_or_404(Complaint, id=id)
    if complaint.author != request.user and not request.user.is_superuser and not request.user.is_staff:
        raise PermissionDenied
    colors = ['text-warning', 'text-danger', 'text-success']

    context = {
        'menu': get_menu_context(request.user.is_authenticated),
        'buttons': False,
    }

    if request.user.is_superuser and complaint.status == complaint.PENDING:
        if request.method == 'POST':
            if request.POST.get('Accepted'):
                complaint.status = 2
            elif request.POST.get('Canceled'):
                complaint.status = 1
            complaint.save()
        else:
            context['buttons'] = True

    context['complaint'] = complaint
    context['status'] = complaint.STATUS_CHOICES[complaint.status][1]
    context['color'] = colors[complaint.status]

    return render(request, 'pages/complaint.html', context)


class VotingSearch(FormView):
    template_name = 'pages/voting_search.html'
    form_class = VotingSearchForm
    success_url = ''

    def form_valid(self, form):
        try:
            voting = Voting.objects.get(id=form.cleaned_data['voting_id'])
            return redirect('voting_page', id=voting.id)
        except Voting.DoesNotExist:
            context = self.get_context_data()
            context['error'] = 'Голосования с таким номером не существует'
            return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super(VotingSearch, self).get_context_data(**kwargs)
        context['pagename'] = 'Найти опрос'
        context['menu'] = get_menu_context(self.request.user.is_authenticated)
        return context


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
        if self.request.user == get_object_or_404(Voting, id=self.kwargs['pk']).author:
            context = super().get_context_data(**kwargs)
            context['pagename'] = 'Редактировать опрос'
            context['menu'] = get_menu_context(self.request.user.is_authenticated)
            return context
        else:
            raise PermissionDenied()
