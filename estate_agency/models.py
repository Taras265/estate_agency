from django.db import models


class BaseModel(models.Model):
    on_delete = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        for field in self._meta.get_fields():
            try:
                if field.auto_created and (field.one_to_many or field.one_to_one):
                    related_manager = getattr(self, field.name)
                    if related_manager.filter(on_delete=False).exists():
                        raise ValueError(
                            f"Cannot delete: related objects exist - {field.name}"
                        )

                if field.auto_created and field.many_to_many:
                    related_manager = getattr(self, field.name)
                    if related_manager.filter(on_delete=False).exists():
                        raise ValueError(
                            f"Cannot delete: related objects exist - {field.name}"
                        )
            except Exception:
                continue

        self.on_delete = True
        self.save()

    class Meta:
        abstract = True
