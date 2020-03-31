from django.contrib.auth.models import User
from scrap.models import Book, Category
from rest_framework import serializers


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class BookSerializer(serializers.HyperlinkedModelSerializer):
    category_id = serializers.HyperlinkedIdentityField(view_name="scrap:category-detail")
    class Meta:
        model = Book
        fields = ('title', 'thumbnail', 'price', 'stock', 'product_description', 'upc', 'category_id')


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')
