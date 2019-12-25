from django.db import models
from django.contrib.auth.models import User

#'Title', 'Poster', 'Genre', 'Director', 'Actors', 'Plot'
class movie_list(models.Model):
    Title = models.CharField(max_length=128)
    Poster = models.CharField(max_length=5000)
    Genre = models.CharField(max_length=128)
    Director = models.CharField(max_length=128)
    Actors = models.CharField(max_length=128)
    Plot = models.CharField(max_length=5000)
    def __str__(self):
        return str(self.id)


class profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars",default="no_profile_pic.png", blank=True)
    create_data = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    def __str__(self):
        return str(self.user_id.id)


class watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.ForeignKey(movie_list, on_delete=models.CASCADE)
    timestamp = models.DateField(auto_now_add=True)

