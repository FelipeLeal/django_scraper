from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from api.serializers import UserSerializer, BookSerializer
from scrap.models import Book
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


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
