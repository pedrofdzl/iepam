from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image

from pathlib import Path
import os

def cv_upload_handler(instance, filename):
    destination = Path('cv')

    extension = str(Path(filename).suffix)
    file = Path(instance.user.username + extension)

    destination = str(destination / file)
    return destination

def profile_pic_upload_handler(instance, filename):
    destination = Path('profile_pics')

    extension = str(Path(filename).suffix)
    file = Path(instance.user.username + extension)

    destination = str(destination / file)
    return destination


def file_extension_validator(value):
    extension = os.path.splitext(value.name)[1]
    
    if not extension.lower() in ['.pdf',]:
        raise ValidationError('Solo se aceptan valores')


# Create your models here.
class ExtendedUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='extended_user')
    second_last_name = models.CharField('Second LastName',max_length=255)
    birthdate = models.DateField("date")
    academic_level = models.CharField('academic Level', max_length=255)
    profile_pic = models.ImageField('profile_pic', upload_to=profile_pic_upload_handler, blank=True, null=True)
    cv = models.FileField('CV', upload_to=cv_upload_handler, blank=True, null=True, validators=[file_extension_validator,])
    canTeach = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Extended User'
        verbose_name_plural = 'Extended Users'

        permissions = [
            ('is_admin', 'Is admin'),
            ('is_teacher', 'Is Teacher'),
            ('is_student', 'Is Student')
        ]

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        img = Image.open(self.profile_pic.path)

        if img.height > 170 or img.width > 170:
            dimensions = (170, 170)
            img.thumbnail(dimensions)
            img.save(self.profile_pic.path)

    
    def __str__(self):
        return str(self.user.username)

    
    def get_full_name(self):
        return f'{self.user.first_name} {self.user.last_name} {self.second_last_name}'
