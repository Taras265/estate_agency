from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from accounts.models import CustomUser
from handbooks.models import Handbook
from utils.const import CHOICES, QUERYSET, LIST_BY_USER, HANDBOOKS_QUERYSET
from django.utils.translation import activate
from django.utils.translation import gettext as _

from utils.mixins.utils import GetQuerysetForMixin


class CustomLoginRequiredMixin(LoginRequiredMixin):
    def get_login_url(self):
        lang = self.kwargs['lang']
        return reverse('accounts:login', kwargs={"lang": lang})


class HandbookListMixin(CustomLoginRequiredMixin, GetQuerysetForMixin):
    paginate_by = 15
    template_name = 'handbooks/list.html'
    # handbook_type = str or None
    # object_columns = list or None

    def get_context_data(self, *, object_list=None, **kwargs):
        user = CustomUser.objects.filter(email=self.request.user).first()
        user_type = user.user_type
        choices = self.choices_by_user()

        activate(self.kwargs['lang'])  # translation
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if user_type in CHOICES.keys() and (handbook_type, handbook_type) in choices:
            context = super().get_context_data(**kwargs)  # load base data
            context['lang'] = self.kwargs['lang']

            context['choice'] = handbook_type
            context.update({'choices': CHOICES[user_type]})

            if context['object_list']:
                if self.object_columns:
                    context['object_values'] = []
                    context['object_columns'] = self.object_columns

                    obj_list = context['object_list'].values()
                    for obj in obj_list:
                        context['object_values'].append(dict())
                        for c in context['object_columns']:
                            context['object_values'][-1].update({c: obj[c]})
                else:
                    context['object_values'] = context['object_list'].values()
                    context['object_columns'] = list(context['object_list'].values()[0])
            else:
                context['object_columns'] = None
            return context
        return self.error_403()

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}

    def choices_by_user(self):
        user_type = CustomUser.objects.filter(email=self.request.user).first().user_type
        return CHOICES[user_type]


class HandbookHistoryListMixin(CustomLoginRequiredMixin, GetQuerysetForMixin):
    template_name = 'handbooks/history_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        user = CustomUser.objects.filter(email=self.request.user).first()
        user_type = user.user_type
        choices = self.choices_by_user()

        activate(self.kwargs['lang'])  # translation
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if user_type in CHOICES.keys() and (handbook_type, handbook_type) in choices:
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
        return self.error_403()


class FormMixin(CustomLoginRequiredMixin):
    template_name = 'form.html'
    success_message = "Success"

    # self.choice_name write in form

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # translation

        handbook_type = self.kwargs.get('handbook_type') or self.choice_name

        if (handbook_type, handbook_type) in self.choices_by_user():
            context = super().get_context_data(**kwargs)
            context['lang'] = self.kwargs['lang']
            return context
        return self.error_403()

    def choices_by_user(self):
        user_type = CustomUser.objects.filter(email=self.request.user).first().user_type
        return CHOICES[user_type]

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}


class SpecialRightFormMixin(FormMixin):
    # write user_field = f'{user field in model}' in view or list
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        user = CustomUser.objects.filter(email=self.request.user).first()
        list_by_user = LIST_BY_USER.get(user.user_type)
        handbook_type = self.choice_name or self.kwargs.get('handbook_type')
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

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj


class DeleteMixin(CustomLoginRequiredMixin):
    template_name = 'delete_form.html'
    success_message = "Success"

    # choice_name

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # translation

        handbook_type = self.kwargs.get('handbook_type') or self.choice_name
        if (handbook_type, handbook_type) in self.choices_by_user():
            context = super().get_context_data(**kwargs)
            context['lang'] = self.kwargs['lang']
            return context
        return self.error_403()

    def post(self, request, *args, **kwargs):
        # messages.success(request, 'message')
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.on_delete = True
        self.object.save()
        return HttpResponseRedirect(success_url)

    def choices_by_user(self):
        user_type = CustomUser.objects.filter(email=self.request.user).first().user_type
        return CHOICES[user_type]

    def error_403(self):
        self.template_name = '403.html'
        return {'lang': self.kwargs['lang']}


class SpecialRightDeleteMixin(DeleteMixin):
    # write user_field = f'{user field in model}' in view
    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        # Next, try looking up by primary key.
        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # Next, try looking up by slug.
        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        user = CustomUser.objects.filter(email=self.request.user).first()
        list_by_user = LIST_BY_USER.get(user.user_type)
        handbook_type = self.choice_name or self.kwargs.get('handbook_type')
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

        # If none of those are defined, it's an error.
        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj
