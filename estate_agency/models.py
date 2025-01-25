from django.db import models


class BaseModel(models.Model):
    on_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True
