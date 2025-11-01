from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('sobre/', views.about, name='about'),
    path('contato/', views.contact, name='contact'),
    path('newsletter/', views.newsletter_signup, name='newsletter_signup'),
    path('privacidade/', views.privacy_policy, name='privacy_policy'),
    path('termos/', views.terms_of_use, name='terms_of_use'),
    path('busca/', views.search, name='search'),
]