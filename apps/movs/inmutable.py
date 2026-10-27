from django.core.exceptions import PermissionDenied
from django.db import models


class InmutableQuerySet(models.QuerySet):

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False,
                update_conflicts=False, **kwargs):
        if update_conflicts:
            raise PermissionDenied("Los registros no se pueden modificar.")
        return super().bulk_create(
            objs, batch_size=batch_size, ignore_conflicts=ignore_conflicts, **kwargs
        )
    
    def update(self, **kwargs):
        raise PermissionDenied("Los registros no se pueden modificar.")

    def delete(self):
        raise PermissionDenied("Los registros no se pueden borrar.")


class InmutableModel(models.Model):
    objects = InmutableQuerySet.as_manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionDenied("Los registros no se pueden modificar.")
        kwargs["force_insert"] = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionDenied("Los registros no se pueden borrar.")