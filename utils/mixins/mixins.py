from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from accounts.models import CustomUser
from handbooks.forms import HandbookForm
from handbooks.models import Handbook
from utils.const import CHOICES, MODEL, LIST_BY_USER, HANDBOOKS_QUERYSET, TABLE_TO_APP, OBJECT_COLUMNS, HANDBOOKS_FORMS
from django.utils.translation import activate

from utils.mixins.utils import GetQuerysetForMixin
from utils.utils import have_permission_to_do


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def get_login_url(self):
        lang = self.kwargs['lang']
        return reverse('accounts:login', kwargs={"lang": lang})


class HandbookListPermissionMixin(CustomLoginRequiredMixin, GetQuerysetForMixin):
    paginate_by = 15
    template_name = 'handbooks/list.html'

    # handbook_type = write handbook_type or none if handbook_type writen in url

    def get_permission_required(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        user = CustomUser.objects.filter(email=self.request.user).first()

        cl_handbook_type = ''.join(handbook_type.split('_'))
        if (handbook_type in LIST_BY_USER.keys() and
                not user.has_perm(f'{TABLE_TO_APP[handbook_type]}.view_{cl_handbook_type}')):
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.view_own_{cl_handbook_type}'
        else:
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.view_{cl_handbook_type}'
        return super().get_permission_required()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # translation

        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        user = CustomUser.objects.filter(email=self.request.user).first()

        context = super().get_context_data(**kwargs)  # load base data
        context['lang'] = self.kwargs['lang']

        context['choice'] = handbook_type
        context.update({'choices': self.choices_by_user(user)})

        context['can_create'] = user.has_perm(f'handbooks.add_{"".join(handbook_type.split("_"))}') or user.has_perm(
            f'objects.add_{"".join(handbook_type.split("_"))}')
        context['can_view_history'] = user.has_perm(
            f'handbooks.view_historical{"".join(handbook_type.split("_"))}') or user.has_perm(
            f'handbooks.view_historical{"".join(handbook_type.split("_"))}')

        if context['object_list']:
            object_columns = OBJECT_COLUMNS.get(handbook_type)
            if object_columns:
                context['object_values'] = []
                context['object_columns'] = object_columns

                obj_list = context['object_list'].values()
                for obj in obj_list:
                    context['object_values'].append(dict())
                    for c in context['object_columns']:
                        context['object_values'][-1].update({c: obj[c]})
                    can_update = have_permission_to_do(user, 'change', handbook_type, obj)
                    can_view_history = have_permission_to_do(user, 'view',
                                                             handbook_type, obj, 'historical')

                    context['object_values'][-1].update({'user_permissions': {'can_update': can_update,
                                                     'can_view_history': can_view_history}})
            else:
                context['object_values'] = context['object_list'].values()

                for obj in context['object_values']:
                    can_update = have_permission_to_do(user, 'change', handbook_type, obj)
                    can_view_history = have_permission_to_do(user, 'view',
                                                             handbook_type, obj, 'historical')

                    obj.update({'user_permissions': {'can_update': can_update,
                                                     'can_view_history': can_view_history}})
                context['object_columns'] = list(context['object_list'].values()[0])
        else:
            context['object_columns'] = None
        return context


class HandbookHistoryListMixin(CustomLoginRequiredMixin, GetQuerysetForMixin):
    template_name = 'handbooks/history_list.html'

    def get_permission_required(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        user = CustomUser.objects.filter(email=self.request.user).first()

        cl_handbook_type = ''.join(handbook_type.split('_'))
        if (handbook_type in LIST_BY_USER.keys() and
                not user.has_perm(f'{TABLE_TO_APP[handbook_type]}.view_historical{cl_handbook_type}')):
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.view_own_historical{cl_handbook_type}'
        else:
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.view_historical{cl_handbook_type}'
        return super().get_permission_required()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # translation

        context = super().get_context_data(**kwargs)  # load base data
        context['lang'] = self.kwargs['lang']

        history = context['object'].history.all()
        changes = []
        for record in history:
            if record.prev_record:
                prev_record = record.prev_record
                for field in context['object']._meta.fields:
                    field_name = field.name
                    old_value = getattr(prev_record, field_name)
                    new_value = getattr(record, field_name)
                    if old_value != new_value:
                        changes.append({
                            'date': record.history_date,
                            'user': record.history_user,
                            'field': field.verbose_name,
                            'old_value': old_value,
                            'new_value': new_value
                        })
        context['history'] = changes
        return context


class FormMixin(CustomLoginRequiredMixin, PermissionRequiredMixin):
    template_name = 'form.html'
    success_message = "Success"

    # write permission_required =

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # translation

        context = super().get_context_data(**kwargs)
        context['lang'] = self.kwargs['lang']

        return context

    def choices_by_user(self):
        user_type = CustomUser.objects.filter(email=self.request.user).first().user_type
        return CHOICES[user_type]

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}


class FormHandbooksMixin(FormMixin):
    # handbook_type = write handbook_type or none if handbook_type writen in url
    # perm_type = 'view' or something like this

    def get_queryset(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if MODEL.get(handbook_type):
            queryset = MODEL[handbook_type].objects.filter(on_delete=False)
            if (handbook_type in LIST_BY_USER.keys() and
                    self.permission_required.find('own')):
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
            return queryset
        return Handbook.objects.filter(type=HANDBOOKS_QUERYSET.get(handbook_type), on_delete=False)

    def get_permission_required(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        user = CustomUser.objects.filter(email=self.request.user).first()

        cl_handbook_type = ''.join(handbook_type.split('_'))
        if (handbook_type in LIST_BY_USER.keys() and
                not user.has_perm(f'{TABLE_TO_APP[handbook_type]}.{self.perm_type}_{cl_handbook_type}')):
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.{self.perm_type}_own_{cl_handbook_type}'
        else:
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.{self.perm_type}_{cl_handbook_type}'

        return super().get_permission_required()

    def get_form(self, form_class=None):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        return super().get_form(HANDBOOKS_FORMS.get(handbook_type) or HandbookForm)

    def get_success_url(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        kwargs = {"lang": self.kwargs['lang']}
        if TABLE_TO_APP[handbook_type] == 'handbooks':
            kwargs.update({"handbook_type": handbook_type})
        return reverse_lazy(f"{TABLE_TO_APP[handbook_type]}:handbooks_list", kwargs=kwargs)


class DeleteMixin(CustomLoginRequiredMixin, PermissionRequiredMixin):
    template_name = 'delete_form.html'
    success_message = "Success"

    # choice_name

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # translation

        context = super().get_context_data(**kwargs)
        context['lang'] = self.kwargs['lang']
        return context

    def post(self, request, *args, **kwargs):
        # messages.success(request, 'message')
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.on_delete = True
        self.object.save()
        return HttpResponseRedirect(success_url)

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


class DeleteHandbooksMixin(DeleteMixin):
    # handbook_type = write handbook_type or none if handbook_type writen in url

    def get_queryset(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if MODEL.get(handbook_type):
            queryset = MODEL[handbook_type].objects.filter(on_delete=False)
            if (handbook_type in LIST_BY_USER.keys() and
                    self.permission_required.find('own')):
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
            return queryset
        return Handbook.objects.filter(type=HANDBOOKS_QUERYSET.get(handbook_type), on_delete=False)

    def get_permission_required(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        user = CustomUser.objects.filter(email=self.request.user).first()

        cl_handbook_type = ''.join(handbook_type.split('_'))
        if (handbook_type in LIST_BY_USER.keys() and
                not user.has_perm(f'{TABLE_TO_APP[handbook_type]}.change_{cl_handbook_type}')):
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.change_own_{cl_handbook_type}'
        else:
            self.permission_required = f'{TABLE_TO_APP[handbook_type]}.change_{cl_handbook_type}'

        return super().get_permission_required()

    """def get_form(self, form_class=None):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        return super().get_form(HANDBOOKS_FORMS.get(handbook_type) or HandbookForm)"""

    def get_success_url(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        kwargs = {"lang": self.kwargs['lang']}
        if TABLE_TO_APP[handbook_type] == 'handbooks':
            kwargs.update({"handbook_type": handbook_type})
        return reverse_lazy(f"{TABLE_TO_APP[handbook_type]}:handbooks_list", kwargs=kwargs)
