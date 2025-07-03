from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class RealEstateImage(models.Model):
    """Зображення обʼєкта нерухомості"""

    image = models.ImageField(upload_to="images/")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        default_permissions = ("add", "change", "view")
        indexes = [models.Index(fields=["content_type", "object_id"])]
