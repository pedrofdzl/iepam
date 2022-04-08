from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from pathlib import Path
import os

def cv_upload_handler(instance, filename):
    destination = Path('cv')

    extension = str(Path(filename).suffix)
    file = Path(instance.user.username + extension)

    destination = str(destination / file)


    return destination


def file_extension_validator(value):
    extension = os.path.splitext(value.name)[1]
    print(extension)
    
    if not extension.lower() in ['.pdf',]:
        raise ValidationError('Solo se aceptan valores')



# Create your models here.
class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extended_user')
    second_last_name = models.CharField('Second LastName',max_length=255)
    birthdate = models.DateField("date")
    academic_level = models.CharField('academic Level', max_length=255)
    cv = models.FileField('CV', upload_to=cv_upload_handler, blank=True, null=True, validators=[file_extension_validator,])

    class Meta:
        verbose_name = 'Extended User'
        verbose_name_plural = 'Extended Users'

        permissions = []
    
    def __str__(self):
        return str(self.user.username)
