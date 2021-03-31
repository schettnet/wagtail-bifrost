import binascii
import os
import uuid

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from private_storage.fields import PrivateFileField


# Django models d
def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


class BifrostFile(models.Model):
    access_token = models.CharField(default=generate_key, max_length=40)
    file = PrivateFileField()
    group = models.CharField(blank=True, null=True, max_length=32)
    ubfn = models.CharField(
        unique=True, default=uuid.uuid4, max_length=32
    )  # unique_bifrost_file_name
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def url(self) -> str:
        return settings.BASE_URL + self.file.url

    @property
    def secure_url(self) -> str:
        return (self.url).replace("://", f"://{self.access_token}@")

    def __str__(self) -> str:
        return self.file.name


@receiver(models.signals.post_delete, sender=BifrostFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


# @receiver(models.signals.pre_save, sender=BifrostFile)
# def auto_delete_file_on_change(sender, instance, **kwargs):
#     print(instance.__dict__)
#     """
#     Deletes old file from filesystem
#     when corresponding `File` object is updated
#     with new file.
#     """
#     if not instance.pk:
#         return False

#     try:
#         old_file = sender.objects.get(pk=instance.pk).file
#     except sender.DoesNotExist:
#         return False

#     new_file = instance.file
#     if not old_file == new_file:
#         if os.path.isfile(old_file.path):
#             os.remove(old_file.path)
