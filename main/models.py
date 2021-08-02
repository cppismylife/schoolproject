from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone


class Voting(models.Model):
    CHECKBOXES, RADIOS, BUTTONS = 0, 1, 2
    TYPE_CHOICES = (
        (CHECKBOXES, "Checkboxes"),
        (RADIOS, "Radios"),
        (BUTTONS, "Buttons"),
    )
    name = models.CharField(max_length=200, blank=False)
    description = models.CharField(max_length=1000)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    type = models.IntegerField(choices=TYPE_CHOICES, default=CHECKBOXES)
    published = models.DateTimeField(default=timezone.now, blank=False)
    finishes = models.DateTimeField(blank=False)
    image = models.ImageField(upload_to='votings', blank=True)
    next_voting = models.OneToOneField(
        "Voting",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='following_voting',
    )
    prev_voting = models.OneToOneField(
        "Voting",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='previous_voting',
    )

    def __str__(self):
        return self.name


class VoteVariant(models.Model):
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.description


class VoteFact(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    variants = models.ManyToManyField(VoteVariant)
    created = models.DateTimeField(default=timezone.now)


class Complaint(models.Model):
    PENDING, CANCELED, ACCEPTED = 0, 1, 2
    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (CANCELED, "Canceled"),
        (ACCEPTED, "Accepted"),
    )
    voting = models.ForeignKey(Voting, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    created = models.DateTimeField(default=timezone.now)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='users', blank=True)


# hook to create UserProfile when creating User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# hook to save profile when saving user
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
