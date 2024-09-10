from django.contrib.auth.mixins import PermissionRequiredMixin

from accounts.models import CustomUser
from handbooks.models import Handbook
from utils.const import MODEL, LIST_BY_USER, HANDBOOKS_QUERYSET, CHOICES, TABLE_TO_APP


class GetQuerysetForMixin(PermissionRequiredMixin):
    """
    Додатковий міксін. Використовуємо для міксінів, де отримаємо дані для справочника
    Якщо ми використовуємо цей міксін, то треба також вказати змінну handbook_type.
    Це має бути або сама назва довідника, або None (якщо є ця змінна в url)
    Ще вказуємо permission_required - які потрібні права.
    """
    paginate_by = 15

    handbook_type = None

    # handbook_type = write handbook_type or none if handbook_type writen in url
    # permission_required = write permission or write permission function

    def get_queryset(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if handbook_type in MODEL:
            queryset = MODEL[handbook_type].objects.filter(on_delete=False)

            if (handbook_type in LIST_BY_USER.keys() and
                    self.permission_required.find('own') != -1):
                user = CustomUser.objects.filter(email=self.request.user).first()
                if isinstance(LIST_BY_USER[handbook_type], str):
                    queryset = queryset.filter(**{LIST_BY_USER[handbook_type]: user})
                else:
                    new_queryset = None
                    for field in LIST_BY_USER[handbook_type]:
                        if new_queryset:
                            new_queryset = new_queryset | queryset.filter(**{field: user})
                        else:
                            new_queryset = queryset.filter(**{field: user})
                    queryset = new_queryset
        else:
            queryset = Handbook.objects.filter(on_delete=False, type=HANDBOOKS_QUERYSET[handbook_type])

        self.queryset = queryset
        return super().get_queryset()

    def choices_by_user(self, user):
        choices = []
        for choice in CHOICES:
            if ((user.has_perm(f'{TABLE_TO_APP[choice[1]]}.view_{choice[1]}')
                 or user.has_perm(f'{TABLE_TO_APP[choice[1]]}.view_own_{choice[1]}'))):
                choices.append(choice)
        return choices

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}
