from urllib.parse import urlencode
from dateutil.relativedelta import relativedelta

from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import BadRequest, PermissionDenied
from django.utils import timezone
from django.utils.translation import activate

from .models import Client, Selection
from .forms import ClientForm, SelectionForm
from .choices import ClientStatusType
from objects.choices import RealEstateStatus
from .services import (
    selection_add_selected_objects,
    ShowingActPDFService,
    ShowingActPDFType,
    get_client_list_context,
    process_selection_form
)
from objects.services import real_estate_model_from_type
from utils.mixins.mixins import (
    CustomLoginRequiredMixin,
    CustomPaginateOnPageMixin,
)
from objects.mixins import DefaultUserInCreateViewMixin
from utils.views import HistoryView


class ClientListView(CustomLoginRequiredMixin,
                    PermissionRequiredMixin,
                    CustomPaginateOnPageMixin,
                    generic.ListView):
    """Список лише тих клієнтів, які доступні поточному користувачу для перегляду."""

    template_name = "clients/client_list.html"
    paginate_by = 10
    permission_required = "clients.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            realtor=self.request.user
        ).select_related("realtor")

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class NewClientListView(CustomLoginRequiredMixin,
                        PermissionRequiredMixin,
                        CustomPaginateOnPageMixin,
                        generic.ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та були додані 1 місяць тому.
    """

    template_name = "clients/client_list.html"
    paginate_by = 10
    permission_required = "clients.view_own_clients"

    def get_queryset(self):
        date_off_add_min = timezone.now() - relativedelta(months=1)
        return Client.objects.filter(
            on_delete=False,
            date_of_add__gte=date_off_add_min,
            realtor=self.request.user
        ).select_related("realtor")

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class InSelectionClientListView(CustomLoginRequiredMixin,
                                PermissionRequiredMixin,
                                CustomPaginateOnPageMixin,
                                generic.ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.IN_SEARCH.
    """

    template_name = "clients/client_list.html"
    paginate_by = 10
    permission_required = "clients.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.IN_SEARCH,
            realtor=self.request.user
        ).select_related("realtor")

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class WithShowClientListView(CustomLoginRequiredMixin,
                             PermissionRequiredMixin,
                             CustomPaginateOnPageMixin,
                             generic.ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.WITH_SHOW.
    """

    template_name = "clients/client_list.html"
    paginate_by = 10
    permission_required = "clients.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.WITH_SHOW,
            realtor=self.request.user
        ).select_related("realtor")

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class DecidedClientListView(CustomLoginRequiredMixin,
                            PermissionRequiredMixin,
                            CustomPaginateOnPageMixin,
                            generic.ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.DECIDED.
    """

    template_name = "clients/client_list.html"
    paginate_by = 10
    permission_required = "clients.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.DECIDED,
            realtor=self.request.user
        ).select_related("realtor")

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class DeferredDemandClientListView(CustomLoginRequiredMixin,
                                   PermissionRequiredMixin,
                                   CustomPaginateOnPageMixin,
                                   generic.ListView):
    """
    Список лише тих клієнтів, які доступні поточному користувачу для перегляду
    та мають статус ClientStatusType.DEFERRED_DEMAND.
    """

    template_name = "clients/client_list.html"
    paginate_by = 10
    permission_required = "clients.view_own_clients"

    def get_queryset(self):
        return Client.objects.filter(
            on_delete=False,
            status=ClientStatusType.DEFERRED_DEMAND,
            realtor=self.request.user
        ).select_related("realtor")

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        extra_context = get_client_list_context(
            self.kwargs["lang"], self.request.user, self.object_list
        )
        context.update(extra_context)
        return context


class ClientCreateView(CustomLoginRequiredMixin,
                       PermissionRequiredMixin,
                       DefaultUserInCreateViewMixin,
                       generic.CreateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/client_form.html"
    permission_required = "clients.add_own_client"

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        # щоб не змінював рієлтора, якщо може створювати лише він
        context["form"].fields["realtor"].widget.attrs["disabled"] = True
        context["form"].fields["realtor"].widget.attrs["readonly"] = True

        return context

    def form_invalid(self, form):
        # щоб не змінював рієлтора, якщо може створювати лише він
        post_data = self.request.POST.copy()
        post_data["realtor"] = self.request.user
        f = self.form_class(post_data)
        if f.is_valid():
            f.save()
            return redirect(self.get_success_url())
        return super().form_invalid(form)

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("clients:all_client_list", kwargs=kwargs)


class ClientUpdateView(CustomLoginRequiredMixin,
                       PermissionRequiredMixin,
                       generic.UpdateView):
    form_class = ClientForm
    template_name = "clients/client_form.html"
    permission_required = "clients.change_own_client"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            raise AttributeError(
                "Generic detail view %s must be called with an object "
                "pk in the URLconf." % self.__class__.__name__
            )
        client = get_object_or_404(Client.objects.select_related(), id=pk, on_delete=False)

        # умова що ми можемо працювати з клієнтом
        if client.realtor != self.request.user:
            raise PermissionDenied()
        return client

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        # щоб не змінював рієлтора, якщо може створювати лише він
        context["form"].fields["realtor"].widget.attrs["disabled"] = True
        context["form"].fields["realtor"].widget.attrs["readonly"] = True
        return context

    def form_invalid(self, form):
        # щоб не змінював рієлтора, якщо може створювати лише він
        o = self.get_object()
        post_data = self.request.POST.copy()
        post_data["realtor"] = self.request.user
        f = self.form_class(post_data, instance=o)
        if f.is_valid():
            f.save()
            return redirect(self.get_success_url())
        return super().form_invalid(form)

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("clients:all_client_list", kwargs=kwargs)


class ClientDeleteView(CustomLoginRequiredMixin,
                       PermissionRequiredMixin,
                       generic.DeleteView):
    template_name = "delete_form.html"
    permission_required = "clients.change_own_client"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if not pk:
            raise AttributeError(
                "Generic detail view %s must be called with an object "
                "pk in the URLconf." % self.__class__.__name__
            )
        client = get_object_or_404(Client, id=pk, on_delete=False)

        # умова що ми можемо працювати з клієнтом
        if client.realtor != self.request.user:
            raise PermissionDenied()
        return client

    def get_context_data(self, *, object_list=None, **kwargs):
        activate(self.kwargs["lang"])
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]
        return context

    def get_success_url(self):
        kwargs = {"lang": self.kwargs["lang"]}
        return reverse_lazy("clients:all_client_list", kwargs=kwargs)


class ClientHistoryView(HistoryView):
    permission_required = "clients.view_own_clients"
    handbook_type = "client"
    perm = "view"
    app = "clients"
    queryset = Client.objects.filter(on_delete=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        # тимчасове рішення,
        # оскільки "handbooks:client_list" було перейменовано на "handbooks:all_client_list"
        context = super().get_context_data(object_list=object_list, **kwargs)
        context["list_url"] = "clients:all_client_list"
        return context


class SelectionListView(CustomLoginRequiredMixin,
                        PermissionRequiredMixin,
                        generic.ListView):
    permission_required = "clients.selection"
    template_name = "clients/selection_list.html"
    context_object_name = "objects"
    form = None
    client = None

    def get_form(self, client):
        if len(self.request.GET) == 0:
            initial_data = {
                "rooms_number": client.rooms_number,
                "locality": client.locality.all(),
                "locality_district": client.locality_district.all(),
                "street": client.street.all(),
                "house": client.house,
                "floor_min": client.floor_min,
                "floor_max": client.floor_max,
                "not_first": client.not_first,
                "not_last": client.not_last,
                "price_from": client.price_from,
                "price_to": client.price_to,
                "square_meter_price_max": client.square_meter_price_max,
                "condition": client.condition.all(),
                "object_type": client.object_type,
            }
            return SelectionForm(initial_data)
        return SelectionForm(self.request.GET)

    def get_queryset(self):
        client_id = self.kwargs.get("client_id")
        self.client = Client.objects.filter(id=client_id).select_related().first()
        if not self.client:
            return []

        if self.client.status == ClientStatusType.IN_SEARCH:
            self.client.status = ClientStatusType.WITH_SHOW
            self.client.save()

        self.form = self.get_form(self.client)
        if not self.form.is_valid():
            return []

        obj_type = int(self.form.cleaned_data.get("object_type"))
        model_class = real_estate_model_from_type(obj_type)
        if not model_class:
            raise BadRequest()

        qs = model_class.objects.filter(
            status__in=(RealEstateStatus.ON_SALE, RealEstateStatus.DEPOSIT)
        ).select_related()
        qs = process_selection_form(qs, self.form)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activate(self.kwargs["lang"])

        objects = []
        for obj in context["objects"]:
            image = obj.images.first()
            objects.append({"image": image, "object": obj})

        context.update({
            "lang": self.kwargs["lang"],
            "client": self.client,
            "form": self.form,
            "objects": objects
        })
        return context


class SelectionHistoryView(CustomLoginRequiredMixin,
                           PermissionRequiredMixin,
                           generic.ListView):
    object_list = Selection.objects.all()
    permission_required = "clients.selection"
    template_name = "clients/selection_history_list.html"
    context_object_name = "objects"

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        context = self.get_context_data()
        context["selections"] = Selection.objects.filter(client_id=pk)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        activate(self.kwargs["lang"])  # Перекладаємо

        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        return context


def showing_act_redirect(request, lang):
    """
    Створення вибірки для клієнта та переадресація на сторінку з актом показу.
    Необхідні query параметри:
    - object_type: int # тип об'єкта нерухомості
    - objects: list[int] # список з id об'єктів
    - client: int # id клієнта
    """
    if request.user.is_anonymous:
        return redirect(reverse_lazy("accounts:login", kwargs={"lang": lang}))

    object_type = int(request.GET.get("object_type"))
    model_class = real_estate_model_from_type(object_type)
    if not model_class:
        raise BadRequest()

    selected_ids = request.GET.getlist("objects")
    objects = model_class.objects.filter(
        ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
        id__in=selected_ids
    )
    for obj in objects:
        obj.in_selection = True
        obj.save()

    client_id = int(request.GET.get("client"))
    client = Client.objects.filter(on_delete=False, id=client_id).first()
    if not client:
        raise BadRequest()

    selection = Selection.objects.create(
        client=client,
        user=request.user,
    )
    selection_add_selected_objects(selection, object_type, *objects)
    selection.save()

    params = request.GET.copy()
    params["objects"] = selected_ids
    url = reverse_lazy("clients:showing_act", kwargs={"lang": lang})
    return redirect(f"{url}?{urlencode(params, doseq=True)}")


class ShowingActView(generic.TemplateView):
    template_name = "clients/showing_act.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lang"] = self.kwargs["lang"]

        object_type = int(self.request.GET.get("object_type"))
        model_class = real_estate_model_from_type(object_type)
        if not model_class:
            raise BadRequest()

        selected_ids = self.request.GET.getlist("objects")
        qs = model_class.objects.filter(
            ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
            id__in=selected_ids
        ).select_related()
        objects = []
        for obj in qs:
            objects.append(
                {
                    "object": obj,
                    "image": obj.images.first(),
                }
            )
        context["objects"] = objects
        context["url"] = f"objects:{model_class._meta.model_name}_showing_act_details"

        return context


def pdf_redirect(request, lang):
    """
    Створення вибірки для клієнта та переадресація на сторінку
    зі створенням pdf-файлу з актом показу.
    Необхідні query параметри:
    - object_type: int # тип об'єкта нерухомості
    - objects: list[int] # список з id об'єктів
    - client: int # id клієнта
    """
    if request.user.is_anonymous:
        return redirect(reverse_lazy("accounts:login", kwargs={"lang": lang}))

    object_type = int(request.GET.get("object_type"))
    model_class = real_estate_model_from_type(object_type)
    if not model_class:
        raise BadRequest()

    selected_ids = request.GET.getlist("objects")
    objects = model_class.objects.filter(
        ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
        id__in=selected_ids
    )
    for obj in objects:
        obj.in_selection = True
        obj.save()

    client_id = int(request.GET.get("client"))
    client = Client.objects.filter(on_delete=False, id=client_id).first()
    if not client:
        raise BadRequest()

    selection = Selection.objects.create(
        client=client,
        user=request.user,
    )
    selection_add_selected_objects(selection, object_type, *objects)
    selection.save()

    params = request.GET.copy()
    params["objects"] = selected_ids
    url = reverse_lazy("clients:generate_pdf", kwargs={"lang": lang})
    return redirect(f"{url}?{urlencode(params, doseq=True)}")


class ShowingActPDFView(CustomLoginRequiredMixin, generic.View):
    def get(self, request, lang):
        """Повертає pdf файл акту показу нерухомості"""
        activate(lang)

        client_id = int(request.GET.get("client"))
        client = Client.objects.filter(on_delete=False, id=client_id).first()
        if not client:
            raise BadRequest()

        object_type = int(self.request.GET.get("object_type"))
        model_class = real_estate_model_from_type(object_type)
        if not model_class:
            raise BadRequest()

        selected_ids = self.request.GET.getlist("objects")
        objects = (
            model_class.objects.filter(
                ~Q(status=RealEstateStatus.COMPLETELY_WITHDRAWN),
                id__in=selected_ids
            )
            .select_related()
        )

        service = ShowingActPDFService()
        buffer = service.generate(ShowingActPDFType.SIMPLE, request.user, client, objects)
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = "attachment; filename=showing_act.pdf"
        return response
