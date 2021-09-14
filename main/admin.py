from django.contrib import admin
from django.contrib.auth.models import User
from .models import Voting, VoteVariant, VoteFact


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name',
                    'last_name', 'is_superuser', 'is_staff')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Voting)
class VotingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'type', 'published', 'finishes', 'next_voting', 'prev_voting')


@admin.register(VoteVariant)
class VoteVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'voting', 'description')


@admin.register(VoteFact)
class VoteFactAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'variants', 'created']
    list_display = ('id', 'user', 'variants_str', 'created')

    @staticmethod
    def variants_str(obj):
        return ', \n'.join([p.description for p in obj.variants.all()])
