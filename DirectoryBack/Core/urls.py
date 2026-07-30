from django.urls import path
from .views import *

urlpatterns = [
    path('auth/sign_up/', SignUp.as_view(), name='sign_up'),
    path('auth/login/', Login.as_view(), name='login'),
    path('home/', Home.as_view(), name='home'),
    path('home/direcotry/', Directories.as_view(), name='directory'),
    path('home/file/', Files.as_view(), name='file'),
    path('home/logout/', UnAuth.as_view(), name='logout'),
]