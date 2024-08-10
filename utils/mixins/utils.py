from accounts.models import CustomUser
from handbooks.models import Handbook
from utils.const import QUERYSET, LIST_BY_USER, HANDBOOKS_QUERYSET, CHOICES


class GetQuerysetForMixin:
    paginate_by = 15
    template_name = 'handbooks/list.html'
    # handbook_type = str or None
    # object_columns = list or None

    def get_queryset(self):
        user = CustomUser.objects.filter(email=self.request.user).first()

        choices = self.choices_by_user()  # load user rights
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')  # load what user want
        if (handbook_type, handbook_type) in choices:  # if user have rules
            if handbook_type in QUERYSET.keys():  # if we need just queryset
                queryset = QUERYSET[handbook_type].objects.filter(on_delete=False)
                list_by_user = LIST_BY_USER.get(user.user_type)
                if list_by_user and \
                        handbook_type in list_by_user.keys():
                    if isinstance(list_by_user[handbook_type], list):
                        new_queryset = None
                        for field in list_by_user[handbook_type]:
                            if new_queryset:
                                new_queryset = new_queryset | queryset.filter(**{field: user})
                            else:
                                new_queryset = queryset.filter(**{field: user})
                        queryset = new_queryset
                    else:
                        queryset = queryset.filter(**{list_by_user[handbook_type]: user})
            if handbook_type in HANDBOOKS_QUERYSET.keys():  # if we need queryset from Handbook model
                queryset = Handbook.objects.filter(on_delete=False,
                                                   type=HANDBOOKS_QUERYSET[self.kwargs['handbook_type']])
                list_by_user = LIST_BY_USER.get(user.user_type)
                if list_by_user and \
                        handbook_type in list_by_user.keys():
                    queryset = queryset.filter(**{list_by_user[handbook_type]: user})
            self.queryset = queryset
            return super().get_queryset()

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}

    def choices_by_user(self):
        user_type = CustomUser.objects.filter(email=self.request.user).first().user_type
        return CHOICES[user_type]
