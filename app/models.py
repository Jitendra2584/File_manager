# from django.db import models


# class Files(models.Model):
#     file=models.FileField(upload_to="uploads/",)

from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User
import uuid


class File(models.Model):
    file=models.FileField(upload_to="uploads/",validators=[FileExtensionValidator(['pdf'])])
    # display_name = models.CharField(max_length=255,default=None)
    display_name = models.ForeignKey(User,on_delete=models.CASCADE)
    filename = models.CharField(max_length=255,default=None)
    unique_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    shared_with = models.ManyToManyField(User, related_name='shared_files', blank=True)
    def __str__(self):
        return self.filename

class Comment(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()

# af2b2e55-2bd8-4fe0-ac8e-0fa3cbcb5e84
# Create your models here.
