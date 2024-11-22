from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from accounts.models import CustomUser
from handbooks.forms import HandbookForm, IdSearchForm
from handbooks.models import Handbook
from objects.forms import HandbooksSearchForm
from utils.const import (CHOICES, MODEL, LIST_BY_USER, HANDBOOKS_QUERYSET, TABLE_TO_APP,
                         OBJECT_COLUMNS, HANDBOOKS_FORMS)
from django.utils.translation import activate

from utils.mixins.utils import GetQuerysetForMixin
from utils.utils import have_permission_to_do


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """
    Використовуємо замість звичайного LoginRequiredMixin, бо в нас трохи інше посилання на
    сторінку входу.
    """

    def get_login_url(self):
        lang = self.kwargs['lang']
        return reverse('accounts:login', kwargs={"lang": lang})


class HandbookListMixin(CustomLoginRequiredMixin, PermissionRequiredMixin):
    paginate_by = 15
    template_name = 'handbooks/list.html'
    context_object_name = 'objects'

    handbook_type = None
    model = None
    form = IdSearchForm
    choices = CHOICES

    custom = False

    def get_queryset(self):
        form = self.form(self.request.GET)
        queryset = self.model.objects.filter(on_delete=False)
        if form.is_valid():
            for field in form.cleaned_data.keys():
                if form.cleaned_data.get(field):
                    queryset = queryset.filter(**{field: form.cleaned_data.get(field)})
        return queryset

    def get_permission_required(self):  # Отримаємо яке нам потрібно право для цієї сторінки
        user = CustomUser.objects.filter(email=self.request.user).first()

        self.permission_required = f'{TABLE_TO_APP[self.handbook_type]}.view_{self.handbook_type}'
        return super().get_permission_required()

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # переклад

        user = CustomUser.objects.filter(email=self.request.user).first()

        # підгружаємо частину готової дати і додаємо що потрібно
        context = super().get_context_data(**kwargs)
        context['lang'] = self.kwargs['lang']
        context['form'] = self.form(self.request.GET)

        context['choice'] = self.handbook_type
        context.update({'choices': self.choices_by_user(user)})

        """
        Ми можемо бачити дату, але, наприклад, не можемо її додавати чи продивлятись історію змін.
        Тому ми тут робимо перевірку
        """
        if not self.custom:
            context['can_create'] = (user.has_perm(f'handbooks.add_{self.handbook_type}')
                                     or user.has_perm(f'objects.add_{self.handbook_type}'))
            context['can_view_history'] = user.has_perm(
                f'handbooks.view_historical{self.handbook_type}') or user.has_perm(
                f'handbooks.view_historical{self.handbook_type}')

        """
        Страшний код, де ми обробляємо список з ДІЙСНО потрібними для клієнта даними 
        (районами, квартирами ітд). Бажано колись спростити, коли буде час.
        """
        if context['object_list']:  # Якщо нам взагалі є з чим працювати
            object_columns = OBJECT_COLUMNS.get(self.handbook_type)
            if object_columns:  # Якщо ми настроіли які дані потрібно відображати в таблиці
                context['object_values'] = []
                context['object_columns'] = object_columns  # Назва стовпців

                obj_list = context['object_list'].values()

                # Переробляємо всі дані для object_values (даних в таблиці), викидуючи те що нам не потрібно
                for obj in obj_list:
                    context['object_values'].append(dict())
                    for c in context['object_columns']:
                        context['object_values'][-1].update({c: obj[c]})

                    # Перевірка що клієнт взагалі щось ще може, крім дивитись на дані
                    can_update = have_permission_to_do(user, 'change', self.handbook_type, obj)
                    can_view_history = have_permission_to_do(user, 'view',
                                                             self.handbook_type, obj, 'historical')
                    if not self.custom:
                        context['object_values'][-1].update({'user_permissions': {'can_update': can_update,
                                                                                  'can_view_history': can_view_history}})
            else:
                # Теж саме, що і в частині коду вище, але нам потрібні всі дані, тож ми нічого не викидуємо
                context['object_values'] = context['object_list'].values()

                for obj in context['object_values']:
                    can_update = have_permission_to_do(user, 'change', self.handbook_type, obj)
                    can_view_history = have_permission_to_do(user, 'view',
                                                             self.handbook_type, obj, 'historical')

                    if not self.custom:
                        obj.update({'user_permissions': {'can_update': can_update,
                                                         'can_view_history': can_view_history}})
                context['object_columns'] = list(context['object_list'].values()[0])
        else:
            context['object_columns'] = None
        return context

    def choices_by_user(self, user):
        choices = []
        for choice in self.choices:
            app = TABLE_TO_APP.get(choice[1]) or 'objects'
            if ((user.has_perm(f'{app}.view_{choice[1]}')
                 or user.has_perm(f'{app}.view_own_{choice[1]}'))):
                choices.append(choice)
        return choices


class HandbooksListMixin(HandbookListMixin):
    def get_queryset(self):
        form = HandbooksSearchForm(self.request.GET)
        queryset = Handbook.objects.filter(on_delete=False, type=HANDBOOKS_QUERYSET[self.handbook_type])
        if form.is_valid():
            if form.cleaned_data.get('id'):
                queryset = queryset.filter(id=form.cleaned_data['id'])
        return queryset


class HandbookOwnPermissionListMixin(HandbookListMixin):
    def get_queryset(self):
        self.queryset = HandbookListMixin.get_queryset(self)

        if self.permission_required.find('own') != -1:
            user = CustomUser.objects.filter(email=self.request.user).first()
            if isinstance(LIST_BY_USER[self.handbook_type], str):
                self.queryset = self.queryset.filter(**{LIST_BY_USER[self.handbook_type]: user})
            else:
                new_queryset = None
                for field in LIST_BY_USER[self.handbook_type]:
                    if new_queryset:
                        new_queryset = new_queryset | self.queryset.filter(**{field: user})
                    else:
                        new_queryset = self.queryset.filter(**{field: user})
                self.queryset = new_queryset
        return self.queryset

    def get_permission_required(self):  # Отримаємо яке нам потрібно право для цієї сторінки
        user = CustomUser.objects.filter(email=self.request.user).first()

        if user.has_perm(f'{TABLE_TO_APP[self.handbook_type]}.view_{self.handbook_type}'):
            self.permission_required = f'{TABLE_TO_APP[self.handbook_type]}.view_{self.handbook_type}'
        else:
            self.permission_required = f'{TABLE_TO_APP[self.handbook_type]}.view_own_{self.handbook_type}'
        print(self.permission_required)
        return (self.permission_required, )


class HandbookWithFilterListMixin(HandbookListMixin):
    filters = []
    queryset_filters = {}
    
    def get_queryset(self):
        f = self.kwargs.get('filter') or list(self.queryset_filters.keys())[0]  # просто вір - так і має бути
        queryset = self.queryset_filters[f].all()
        if queryset.model != self.model:
            self.model = queryset.model
        return queryset
    
    def get_context_data(self, *, object_list=None, **kwargs):
        f = self.kwargs.get('filter') or list(self.queryset_filters.keys())[0]  # просто вір - так і має бути

        context = super().get_context_data(**kwargs)
        context['filters'] = self.filters
        context['filter'] = f
        context['app'] = TABLE_TO_APP[context['choice']]

        return context


class HandbookHistoryListMixin(CustomLoginRequiredMixin, GetQuerysetForMixin):
    """
    Міксін для виводу історії змін данних (з назви думаю логічно)
    """
    template_name = 'handbooks/history_list.html'

    def get_permission_required(self):  # Отримаємо яке нам потрібно право для цієї сторінки
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
        activate(self.kwargs['lang'])  # Переклад

        context = super().get_context_data(**kwargs)  # Підгружаємо дані
        context['lang'] = self.kwargs['lang']

        # Додаємо дані з історії змін
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
    """
    Використовуємо для будь якої ЗВИЧАЙНОЇ сторінки з формочкою або наслідумось для
    написання сторніки з специфічною формочкою.
    Маємо вказати permission_required (яке требо прова для цієї сторінки)
    """
    template_name = 'form.html'
    success_message = "Success"

    # write permission_required =

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs['lang'])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context['lang'] = self.kwargs['lang']

        return context


class FormHandbooksMixin(FormMixin):
    """
    Міксін для спеціфічної формочки довідника. Використовуємо для додавання чи зміни даних довідника.
    Якщо ми використовуємо цей міксін, то треба також вказати змінну handbook_type.
    Це має бути або сама назва довідника, або None (якщо є ця змінна в url)
    Також вказуэмо perm_type - який треба рівень дозволу (view, change, add)
    """
    # handbook_type = write handbook_type or none if handbook_type writen in url
    # perm_type = 'view' or something like this

    def get_queryset(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if MODEL.get(handbook_type):
            queryset = MODEL[handbook_type].objects.filter(on_delete=False)
            if (handbook_type in LIST_BY_USER.keys() and
                    self.permission_required.find('own') >= 0):
                user = CustomUser.objects.filter(email=self.request.user).first()
                if isinstance(LIST_BY_USER[handbook_type], str):
                    queryset = queryset.filter(**{LIST_BY_USER[handbook_type]: user})
                else:
                    new_queryset = None
                    for field in LIST_BY_USER[handbook_type]:
                        if new_queryset:
                            # Об'єднуємо кверісети
                            new_queryset = new_queryset | queryset.filter(**{field: user})
                        else:
                            new_queryset = queryset.filter(**{field: user})
                    queryset = new_queryset
            return queryset
        return Handbook.objects.filter(type=HANDBOOKS_QUERYSET.get(handbook_type), on_delete=False)

    def get_permission_required(self):  # Отримаємо яке нам потрібно право для цієї сторінки
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
        return reverse_lazy(f"{TABLE_TO_APP[handbook_type]}:{handbook_type}_list", kwargs=kwargs)


class DeleteMixin(CustomLoginRequiredMixin, PermissionRequiredMixin):
    """
    Використовуємо для будь якого видалення даних або наслідумось для
    написання сторніки з специфічною формочкою.
    Маємо вказати permission_required (яке требо прова для цієї сторінки)

    УВАГА!!! МИ НЕ ВИДАЛЯЄМО ДАНІ НАЗАВЖДИ!!!
    """
    template_name = 'delete_form.html'
    success_message = "Success"

    # permission_required =

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


class DeleteHandbooksMixin(DeleteMixin):
    """
        Міксін для видаленя даних з довідника довідника.
        Якщо ми використовуємо цей міксін, то треба також вказати змінну handbook_type.
        Це має бути або сама назва довідника, або None (якщо є ця змінна в url)

        УВАГА!!! МИ НЕ ВИДАЛЯЄМО ДАНІ НАЗАВЖДИ!!!
        """
    # handbook_type = write handbook_type or none if handbook_type writen in url

    def get_queryset(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        if MODEL.get(handbook_type):
            queryset = MODEL[handbook_type].objects.filter(on_delete=False)
            if (handbook_type in LIST_BY_USER.keys() and
                    self.permission_required.find('own') >= 0):
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

    def get_success_url(self):
        handbook_type = self.handbook_type or self.kwargs.get('handbook_type')
        kwargs = {"lang": self.kwargs['lang']}
        if TABLE_TO_APP[handbook_type] == 'handbooks':
            kwargs.update({"handbook_type": handbook_type})
        return reverse_lazy(f"{TABLE_TO_APP[handbook_type]}:{handbook_type}_list", kwargs=kwargs)
