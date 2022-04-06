from tabnanny import verbose
from django.db import models
from django.contrib.auth.models import User

from pathlib import Path

def cv_upload_handler(instance, filename):
    destination = Path('cv')

    extension = Path(filename).suffix

    destination = str(destination / instance.username / extension)

    return destination


# Create your models here.
class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extended_user')
    second_last_name = models.CharField('Second LastName',max_length=255)
    birthdate = models.DateField("date")
    academic_level = models.CharField('academic Level', max_length=255)
    cv = models.FileField('CV', upload_to=cv_upload_handler, blank=True, null=True)

    class Meta:
        verbose_name = 'Extended User'
        verbose_name_plural = 'Extended Users'

        permissions = []
    
    def __str__(self):
        return str(self.user.username)
