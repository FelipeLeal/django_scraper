from django.shortcuts import render
from .models import Book


def index(request) -> render:
    books = Book.objects.all()
    context = {'books': books}
    return render(request, 'index.html', context)



