import datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime

from main.forms import InputForm
from main.models import Voting, VoteVariant, User


def get_forms(context, request):
    for accord_num in ['1', '2', '3']:
        for i in range(1, context['accordion_context'][accord_num]['count'] + 1):
            context['accordion_context'][accord_num]['forms'].append(
                InputForm(request.POST, prefix=str(i) + accord_num))
    return context['accordion_context'][context['type_of']]['forms']


def check_valid_and_create(context, forms, request, voteinfo):
    flag = True
    for form in forms:
        if not form.is_valid():
            flag = False
    if flag and voteinfo.is_valid() and \
        timezone.now() < \
        parse_datetime(voteinfo.data['start_time']).astimezone() + datetime.timedelta(minutes=3) < \
        parse_datetime(voteinfo.data['finish_time']).astimezone() + datetime.timedelta(minutes=3):
        try:
            voting = Voting(author=request.user,
                            name=voteinfo.cleaned_data['name'],
                            description=voteinfo.cleaned_data['desc'],
                            type=int(context['type_of']) - 1,
                            image=voteinfo.files['image'],
                            published=voteinfo.cleaned_data['start_time'],
                            finishes=voteinfo.cleaned_data['finish_time'])
        except KeyError:
            voting = Voting(author=request.user,
                            name=voteinfo.cleaned_data['name'],
                            description=voteinfo.cleaned_data['desc'],
                            type=int(context['type_of']) - 1,
                            published=voteinfo.cleaned_data['start_time'],
                            finishes=voteinfo.cleaned_data['finish_time'])
        voting.save()
        context['v_id'] = voting.id
        for i in range(1, context['accordion_context'][context['type_of']]['count'] + 1):
            var = VoteVariant(voting=voting, description=forms[i - 1].data[str(i) + context['type_of'] + '-var'])
            var.save()
    else:
        context['error'] = True
        flag = False
    return flag


def check_eligible_to_vote(voting: Voting, request) -> bool:
    if request.session.get('votes'):
        if voting.id in request.session.get('votes'):
            return False

    # validate that voting is active
    if not (voting.published < timezone.now() < voting.finishes):
        return False

    # validate that user has not voted on this Voting before
    for vote_variant in voting.votevariant_set.all():
        vote_variant: VoteVariant = vote_variant
        if request.user.is_authenticated:
            if vote_variant.votefact_set.filter(user=request.user).count() != 0:
                return False

    return True
