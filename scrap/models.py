from django.contrib import admin
from django.db import models


# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=255)
    thumbnail = models.URLField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    product_description = models.TextField()
    upc = models.CharField(max_length=255)
    category_id = models.ForeignKey('Category', on_delete=models.CASCADE)


class Category(models.Model):
    title = models.CharField(max_length=255)

admin.site.register(Book)
admin.site.register(Category)