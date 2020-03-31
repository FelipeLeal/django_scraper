from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Book


def index(request) -> render:
    books_list = Book.objects.all()
    paginator = Paginator(books_list, 25)  # Show 25 books per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'index.html', {'page_obj': page_obj})



