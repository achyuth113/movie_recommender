from .models import *
from rest_framework import serializers


class MovieSerialiser(serializers.ModelSerializer):
    class Meta:
        model = movie_list
        fields = ['Poster','id','Title']

