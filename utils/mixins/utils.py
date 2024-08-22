from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Permission

from accounts.models import CustomUser
from handbooks.models import Handbook, Client
from utils.const import MODEL, LIST_BY_USER, HANDBOOKS_QUERYSET, CHOICES


class GetQuerysetForMixin:
    paginate_by = 15

    handbook_type = None
    # handbook_type = write handbook_type or none if handbook_type writen in url

    def get_queryset(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if handbook_type in MODEL:
            queryset = MODEL[handbook_type].objects.filter(on_delete=False)
        else:
            queryset = Handbook.objects.filter(on_delete=False, type=HANDBOOKS_QUERYSET[handbook_type])

        """
        user = CustomUser.objects.filter(email=self.request.user).first()
        if self.permission_required.find('own') and self.user_fields:
            if len(self.user_fields) > 1:
                new_queryset = queryset.filter(**{self.user_fields[0]: user})
            else:
                new_queryset = None
                for field in self.user_fields:
                    if new_queryset:
                        new_queryset = new_queryset | queryset.filter(**{field: user})
                    else:
                        new_queryset = queryset.filter(**{field: user})
                queryset = new_queryset"""

        self.queryset = queryset
        return super().get_queryset()

    def choices_by_user(self, user):
        choices = []
        for choice in CHOICES:
            if (user.has_perm(f'handbooks.view_{choice[1]}')
                    or user.has_perm(f'handbooks.view_own_{choice[1]}')):
                choices.append(choice)
        return choices

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}
