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
        parse_datetime(voteinfo.data['start_time']).astimezone() < \
        parse_datetime(voteinfo.data['finish_time']).astimezone():
        try:
            voting = Voting(author=request.user,
                            name=voteinfo.data['name'],
                            description=voteinfo.data['desc'],
                            type=int(context['type_of']) - 1,
                            image=voteinfo.files['image'],
                            published=voteinfo.data['start_time'],
                            finishes=voteinfo.data['finish_time'])
        except:
            voting = Voting(author=request.user,
                            name=voteinfo.data['name'],
                            description=voteinfo.data['desc'],
                            type=int(context['type_of']) - 1,
                            published=voteinfo.data['start_time'],
                            finishes=voteinfo.data['finish_time'])
        voting.save()
        context['v_id'] = voting.id
        for i in range(1, context['accordion_context'][context['type_of']]['count'] + 1):
            var = VoteVariant(voting=voting, description=forms[i - 1].data[str(i) + context['type_of'] + '-var'])
            var.save()
    else:
        context['error'] = True
        flag = False
    return flag


def check_eligible_to_vote(voting: Voting, user: User) -> bool:

    if user.is_anonymous:
        return False

    # validate that user isn't the Voting author
    if voting.author == user:
        return False

    # validate that voting is active
    if not (voting.published < timezone.now() < voting.finishes):
        return False

    # validate that user has not voted on this Voting before
    for vote_variant in voting.votevariant_set.all():
        vote_variant: VoteVariant = vote_variant

        if vote_variant.votefact_set.filter(user=user).count() != 0:
            return False

    return True
