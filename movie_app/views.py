from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.views.generic import ListView,DetailView
from django.shortcuts import *
from .models import *
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout,update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.db.models import Q
from .forms import *
import pandas  as pd
from rake_nltk import Rake
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from imdb import IMDb
def get_dataframe(T,G,P):
    movielist = []
    strings = G.split(",")
    for string in strings:
        print(string)
        queryset = list(movie_list.objects.values('id', 'Title', 'Genre', 'Director', 'Actors', 'Plot').filter(Genre__icontains=string))
        movielist = movielist + queryset
    plot = P
    r = Rake()
    r.extract_keywords_from_text(plot)
    key_words_dict_scores = r.get_word_degrees()
    strings = list(key_words_dict_scores.keys())
    strings = strings[0:3]
    for string in strings:
        queryset = list(movie_list.objects.values('id', 'Title', 'Genre', 'Director', 'Actors', 'Plot').filter(
            Plot__icontains=string))
        movielist = movielist + queryset
    print(movielist)

    pass

def get_recommendations1(T,G,P):
    queryset=[]
    for i in list(movie_list.objects.values('id', 'Title', 'Genre', 'Director', 'Actors', 'Plot').all()):
        queryset.append([i['id'],i['Title'],i['Genre'], i['Director'], i['Actors'], i['Plot']])
    queryset.append([10000,T,G,'AB','AB',P])
    data_set = pd.DataFrame(queryset,columns=['id','Title', 'Genre', 'Director', 'Actors', 'Plot'])
    print(data_set.head(10))
    data_set['Key_words'] = ""
    for index, row in data_set.iterrows():
        plot = row['Plot']
        r = Rake()
        r.extract_keywords_from_text(plot)
        key_words_dict_scores = r.get_word_degrees()
        row['Key_words'] = list(key_words_dict_scores.keys())

    data_set.drop(columns=['Plot'], inplace=True)
    data_set.set_index('id', inplace=True)
    columns = data_set.columns
    temp=[]
    for index, row in data_set.iterrows():
        words = ''
        for col in columns:
            if col == 'id' or col == 'Title':
                words=words
            elif col != 'Director':
                words = words + ' '.join(row[col]) + ' '
            else:
                words = words + row[col] + ' '
        temp.append(words)
    data_set['bag_of_words'] = temp
    data_set.drop(columns=[col for col in data_set.columns if col != 'bag_of_words'], inplace=True)
    #print(data_set.head(10))
    count = CountVectorizer()
    count_matrix = count.fit_transform(data_set['bag_of_words'])

    indices = pd.Series(data_set.index)
    indices[:5]
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    # cosine_sim
    recommended_movies = []
    idx = indices[indices == 10000].index[0]
    #print(idx)
    score_series = pd.Series(cosine_sim[idx]).sort_values(ascending=False)
    top_20_indexes = list(score_series.iloc[2:22].index)
    print(top_20_indexes)
    for i in top_20_indexes:
        recommended_movies.append(list(data_set.index)[i])
    return recommended_movies


def get_recommendations(T,G,P):
    queryset=[]
    T=str(T)
    G=str(G)
    P=str(P)
    T=T[T.find('value='):]
    T=T[:T.find('" max')]
    T=T[7:]
    G = G[G.find('value='):]
    G = G[:G.find('" max')]
    G = G[7:]
    P=P[P.find('value='):]
    P=P[:P.find('" max')]
    P=P[7:]
    T=T.lower()
    P=P.lower()
    G=G.lower()
    print(T+G+P)
    queryset.append([T, G, 'AB', 'AB', P])
    for i in list(movie_list.objects.values('Title', 'Genre', 'Director', 'Actors', 'Plot').all()):
        queryset.append([i['Title'],i['Genre'], i['Director'], i['Actors'], i['Plot']])
    data_set = pd.DataFrame(queryset,columns=['Title', 'Genre', 'Director', 'Actors', 'Plot'])
    #print(data_set.head(10))
    data_set['Key_words'] = ""

    for index, row in data_set.iterrows():
        plot = row['Plot']
        r = Rake()
        r.extract_keywords_from_text(plot)
        key_words_dict_scores = r.get_word_degrees()
        row['Key_words'] = list(key_words_dict_scores.keys())

    data_set.drop(columns=['Plot'], inplace=True)
    data_set.set_index('Title', inplace=True)
    data_set['bag_of_words'] = ''
    columns = data_set.columns
    for index, row in data_set.iterrows():
        words = ''
        for col in columns:
            if col == 'Key_words':
                words = words + ' '.join(row[col]) + ' '
            else:
                words = words + row[col] + ' '
        row['bag_of_words'] = words

    data_set.drop(columns=[col for col in data_set.columns if col != 'bag_of_words'], inplace=True)
    # print(data_set.head(10))
    count = CountVectorizer()
    count_matrix = count.fit_transform(data_set['bag_of_words'])
    print(count_matrix)
    indices = pd.Series(data_set.index)
    indices[:5]
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    # cosine_sim
    print(cosine_sim)
    recommended_movies = []
    idx = indices[indices == T].index[0]
    #print(idx)
    score_series = pd.Series(cosine_sim[idx]).sort_values(ascending=False)
    top_10_indexes = list(score_series.iloc[2:12].index)
    print(top_10_indexes)
    for i in top_10_indexes:
        recommended_movies.append(list(data_set.index)[i])
    return recommended_movies

def get_string(name_list):
    s=''
    for name in name_list:
        s=s+name+' '
    s=s[:3000]
    return s.lower()

class TempView(View):
    #< QueryDict: {'csrfmiddlewaretoken': ['VOwHtalBzZz2kEuCh8m0KoJhQE17D5HlThXocLbwNaUIyJIm8KgrZWEo2uVK1frn'],
     #             'username': ['te'], 'first_name': ['te'], 'email': ['te@gmail.com'], 'password': ['te@123']} >

    def get(self, request, *args, **kwargs):
        f=open("C:\PythonCourse\mj_project\LLL.csv","r")
        for temp in f.readlines():
            temp=temp.strip()
            items=list(temp.split("???"))
            print(len(items))
            form=MovieForm(data=None)
            
            movie_form=form.save(commit=False)
            movie_form.Title=items[0]
            movie_form.Genre=items[1].lower()
            movie_form.Actors=items[2]
            movie_form.Director=items[3]
            movie_form.Plot=items[4]
            movie_form.Poster=items[5]
            movie_form.save()
        return redirect("movie_app:login_form")


class SignupView(View):
    def get(self,request,*args,**kwargs):
        userform=SignupForm
        return render(request, template_name='accounts/signup_form.html', context={'userform':userform})
    def post ( self, request, *args, **kwargs ):
        form=SignupForm(request.POST)
        print(request.POST)
        if form.is_valid():
            user=User.objects.create_user(**form.cleaned_data)
            user.save()
            profile_form=ProfileForm(data=None)
            profiles=profile_form.save(commit=False)
            profiles.user_id=user
            profiles.save()
        return redirect("movie_app:login_form")

class LoginView(View):
    def get(self,request,*args,**kwargs):
        loginform=LoginForm
        return render(request, template_name='accounts/login_form.html', context={'loginform':loginform})
    def post ( self, request, *args, **kwargs ):
        form=LoginForm(request.POST)
        if form.is_valid ():
            user = authenticate ( username=form.cleaned_data['username'],
                                  password=form.cleaned_data['password'] )
            if user !=None:
                login(request,user)
                return redirect("movie_app:watchlist",request.user.id)
        return redirect("movie_app:login_form")


class LogOutView(View):
    def get( self, request: object ) -> object:
        logout(request)
        return redirect("movie_app:login_form")

class DetailAccountView(LoginRequiredMixin,DetailView):
    login_url = '/users/login/'
    context_object_name = 'userform'
    def get(self, request, *args, **kwargs):
        userform = User.objects.values('id', 'first_name', 'username', 'email').filter(id=kwargs['pk'])[0]
        profileform = profile.objects.all().filter(user_id=userform['id'])[0]
        watchlist_count = watchlist.objects.all().filter(user_id=kwargs['pk']).count()
        userform['watchlist_count']=watchlist_count
        userform['profile'] = profileform
        return render(request, template_name='accounts/account_detail.html',
                      context={'userform': userform, 'id': int(request.user.id)})


class UpdateAccountView(LoginRequiredMixin,UpdateView):
    login_url = '/movie_app/login/'
    model = profile
    template_name='accounts/add_user_profile.html'
    def get(self, request, *args, **kwargs):
        if int(request.user.id) != int(kwargs['pk']):
            return redirect("movie_app:update", request.user.id)
        myprofile = profile.objects.get(user_id=request.user.id)
        form = ProfileForm(instance=myprofile)
        details=profile.objects.all().filter(user_id=request.user.id)[0]
        return render(request, self.template_name, {'profiledetails': details,'profileform': form,'id': (request.user.id)})
    def post(self, request, *args, **kwargs):
        instance = profile.objects.get(user_id=request.user.id)
        form = ProfileForm(request.POST,request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("movie_app:profile", request.user.id)
        return redirect('movie_app:profile', request.user.id)

class MovieDetailsView(LoginRequiredMixin,ListView):
    login_url = '/movie_app/login/'
    def get(self, request, *args, **kwargs):
        form = movie_list.objects.all().filter(id=int(kwargs['pk']))[0]
        userform=[{'form':form,'follw':watchlist.objects.all().filter(user_id=request.user, movie_id=form).count()}]
        return render(request, template_name='accounts/account_list.html',
                      context={'title':"Movie Details",'userform': userform, 'id': int(request.user.id)})

class RecommendView(LoginRequiredMixin,View):
    model=movie_list
    template_name = 'accounts/movie_form.html'
    def get(self,request,*args,**kwargs):
        form=MovieForm
        return render(request, template_name='accounts/movie_form.html', context={'form':form,'id':int(request.user.id)})
    def post ( self, request, *args, **kwargs ):
        form1=MovieForm(request.POST)
        result=get_recommendations(str(form1['Title']),str(form1['Genre']),str(form1['Plot']))
        print(result)
        form = list(movie_list.objects.all().filter(Title__in=result))
        userform = []
        for element in form:
            name1=element.Title
            name2=str(form1['Title'])
            if name1.lower()!=name2.lower():
                userform.append({'form': element,
                             'follow': watchlist.objects.all().filter(user_id=request.user, movie_id=element).count()})
        return render(request, template_name='accounts/account_list.html',
                      context={'title': "Recommended Movies", 'userform': userform, 'id': int(request.user.id)})

class WatchListView(LoginRequiredMixin,ListView):
    login_url = '/movie_app/login/'
    def get(self, request, *args, **kwargs):
        user_id = User.objects.all().filter(id=kwargs['pk'])[0]
        list_of_movies = list(
            item['movie_id'] for item in list(watchlist.objects.values('movie_id').filter(user_id=user_id)))
        form = list(movie_list.objects.all().filter(id__in=list_of_movies))
        userform=[]
        for element in form:
            userform.append({'form':element,'follow':watchlist.objects.all().filter(user_id=request.user, movie_id=element).count()})
        return render(request, template_name='accounts/account_list.html',
                      context={'title':"WatchList Movies",'userform': userform, 'id': int(request.user.id)})


@login_required
def change_password(request, *args, **kwargs):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

@login_required
def add_watchlist_view(request, *args, **kwargs):
    try:
        follower = User.objects.get(id=request.user.id)
        followings = movie_list.objects.get(id=kwargs['pk'])
    except User.DoesNotExist:
        messages.warning(
            request,
            'requested user is not a registered user.'
        )
        return HttpResponseRedirect(reverse_lazy('home'))
    created = watchlist.objects.get_or_create(
            user_id=follower,
            movie_id=followings
        )
    if (created):
        messages.success(
                request,
                'You\'ve successfully followed.'
        )
    else:
        messages.warning(
                request,
                'You\'ve already followed.'
            )
    return HttpResponseRedirect(
        reverse_lazy(
            'movie_app:watchlist',
            kwargs={'pk': int(request.user.id)}
        )
    )


@login_required
def remove_watchlist_view(request, *args, **kwargs):
    try:
        follower = User.objects.get(id=request.user.id)
        followings = movie_list.objects.get(id=kwargs['pk'])
        status = watchlist.objects.filter(user_id=follower, movie_id=followings).delete()
        print(status)
        messages.success(
            request,
            'You\'ve just unfollowed.'
        )
    except User.DoesNotExist:
        messages.warning(
            request,
            'Requested user is not a registered user.'
        )
        return HttpResponseRedirect(reverse_lazy('users:profile',kwargs={'pk': int(request.user.id)}))
    except follower.DoesNotExist:
        messages.warning(
            request,
            'You didn\'t follow this person.'
        )
    return HttpResponseRedirect(
        reverse_lazy(
            'movie_app:watchlist',
            kwargs={'pk': int(request.user.id)}
        )
    )

