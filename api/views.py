from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from api.serializers import UserSerializer, BookSerializer
from scrap.models import Book, Category
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
import re


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class BookViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = BookSerializer

    @action(detail=False, methods=['get'])
    def catalog(self, request):
        # Only to use request
        if request.method == 'GET':
            queryset = Book.objects.all()
            serializer = BookSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)

    @action(detail=False, methods=['put'])
    def update_catalog(self, request) -> HttpResponse:
        categories = get_categories()
        for category in categories:
            Category.objects.get_or_create(title=category)

        books_list = get_books_data()
        first_part = books_list[:len(books_list) // 2]
        second_part = books_list[len(books_list) // 2:]
        if all([save_books(first_part), save_books(second_part)]):
            return HttpResponse('')
        else:
            # my case
            return HttpResponse(status=408)


def save_books(book_list: list) -> bool:
    try:
        for books in book_list:
            category_model = Category.objects.get(title=books['category'])
            Book.objects.get_or_create(title=books['title'], thumbnail=books['thumbnail'], price=books['price'],
                                       stock=books['stock'], product_description=books['product_description'],
                                       upc=books['upc'], category_id=category_model)
    except Exception:
        return False
    return True


def get_books_data() -> list:
    get_books = get_books_urls_by_page()
    first_part = get_books[:len(get_books) // 2]
    second_part = get_books[len(get_books) // 2:]
    data = []
    for url in first_part:
        data.append(append_data(url))
    for url in second_part:
        data.append(append_data(url))
    return data


def append_data(url):
    soup = get_and_parse_url(url)
    p_desc_find = soup.find('div', id='product_description')
    img = soup.find('img')
    p_desc = "" if not p_desc_find else p_desc_find.find_next('p').text
    site = urlparse(url)
    thumbnail = "" if not img else site.scheme + '://' + site.netloc + img.get('src').replace('../../', '/')
    return {
        'category': re.sub('^\d', "", soup.find('a', href=re.compile('/category/books/')).string),
        'title': soup.find('div', {'class': re.compile("product_main")}).h1.text,
        'thumbnail': thumbnail,
        'price': soup.find('p', {'class': 'price_color'}).text[1:],
        'stock': re.sub('[^0-9]', "", soup.find('p', {'class': 'instock availability'}).text),
        'product_description': p_desc,
        'upc': soup.find('table', {'class': 'table table-striped'}).find_next('td').text
    }


def get_categories() -> list:
    content = requests.get('http://books.toscrape.com/index.html', verify=False).content
    soup = BeautifulSoup(content, 'html.parser')
    categories = [category.get_text().strip() for category in
                  soup.find_all(href=re.compile('catalogue/category/books/'))]
    return categories


def get_and_parse_url(url) -> BeautifulSoup:
    result = requests.get(url, verify=False).content
    return BeautifulSoup(result, 'html.parser')


def get_books_urls(url) -> list:
    soup = get_and_parse_url(url)
    return (["/".join(url.split("/")[:-1]) + "/" + book.div.a.get('href') for book in
             soup.findAll('article', {'class': 'product_pod'})])


def get_books_urls_by_page() -> list:
    pages_urls = []
    books_urls = []
    new_page = 'http://books.toscrape.com/catalogue/page-1.html'
    while requests.get(new_page).status_code == 200:
        pages_urls.append(new_page)
        new_page = pages_urls[-1].split("-")[0] + "-" + str(
            int(pages_urls[-1].split("-")[1].split(".")[0]) + 1) + '.html'
    for page in pages_urls:
        books_urls.extend(get_books_urls(page))
    return books_urls
