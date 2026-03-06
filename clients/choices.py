from django.db import models
from django.utils.translation import gettext_lazy as _


class IncomeSourceType(models.IntegerChoices):
    RECOMMENDATIONS = 1, _("Recommendations")
    SELLER = 2, _("Seller")  # Продавець
    INTERNET = 3, _("Internet")
    VISITOR = 4, _("Visitor")
    BANNER = 5, _("Banner")
    POSTING = 6, _("Posting")  # Расклейка


class ClientStatusType(models.IntegerChoices):
    IN_SEARCH = 1, _("In search")
    WITH_SHOW = 2, _("With a show")
    DECIDED = 3, _("Decided")
    DEFERRED_DEMAND = 4, _("Deferred demand")