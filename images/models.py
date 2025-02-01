from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class RealEstateImage(models.Model):
    """Зображення обʼєкта нерухомості"""
    image = models.ImageField(upload_to="images/")
    on_delete = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        default_permissions = ("add", "change", "view")
        indexes = [
            models.Index(fields=["content_type", "object_id"])
        ]
