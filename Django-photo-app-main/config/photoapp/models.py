'''Photoapp Models'''

from django.contrib.auth import get_user_model
from django.db import models
from taggit.managers import TaggableManager


class Photo(models.Model):
    
    title = models.CharField(max_length=45)
    
    description = models.CharField(max_length=250) 

    created = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='photo/')

    submitter = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    tags = TaggableManager() 

    def __str__(self):
        return self.title
    
class Image(models.Model):
    file = models.ImageField(upload_to='images/')
    stored = models.BooleanField(default=False)
    
    def __str__(self):
        return self.file.name