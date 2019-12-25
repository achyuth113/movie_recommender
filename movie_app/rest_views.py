from rest_framework import generics
from .serialisers import *
from django.contrib.auth.models import User

class SearchApi(generics.ListCreateAPIView):
    serializer_class = MovieSerialiser
    def get_queryset(self):
        userid=list(item['id'] for item in list(movie_list.objects.values('id').filter(Title__icontains=self.kwargs['slug'])))
        queryset = movie_list.objects.all().filter(id__in=userid)
        out_queryset =MovieSerialiser(queryset,many=True)
        out=out_queryset.data[:]
        return out
