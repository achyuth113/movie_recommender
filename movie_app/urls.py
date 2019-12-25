from django.urls import path
from django.conf.urls import url
from .views import *
from .rest_views import *
app_name = "movie_app"

urlpatterns = [
    #url(r'^temp/$', TempView.as_view(), name='temp_form'),
    url(r'^signup/$', SignupView.as_view(), name='signup_form'),
    url(r'^login/$', LoginView.as_view(), name='login_form'),
    url(r'^logout/$', LogOutView.as_view(), name='logout_form'),
    url(r'profile/(?P<pk>\d+)/$', DetailAccountView.as_view(), name='profile'),
    url(r'movie_details/(?P<pk>\d+)/$', MovieDetailsView.as_view(), name='movie_profile'),
    url(r'update/(?P<pk>\d+)/$',UpdateAccountView.as_view(),name='update'),
    url(r'update/password/(?P<pk>\d+)/$',change_password,name='change_password'),
    url(r'following/(?P<pk>\d+)/$',WatchListView.as_view(),name='watchlist'),
    url(r'follow/(?P<pk>\d+)/$',add_watchlist_view,name='add'),
    url(r'(?P<pk>\d+)/unfollow/$',remove_watchlist_view,name='remove'),
    url(r'^recommend/$', RecommendView.as_view(), name='recommend'),
    path('movie/api/<slug:slug>', SearchApi.as_view(), name="search_api"),

]

