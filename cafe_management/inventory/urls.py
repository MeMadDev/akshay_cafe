# urls.py
from django.urls import path
from .views import user_login, home, user_logout, create_bill, previous_bills

urlpatterns = [
    path('', user_login, name='login'),
    path('home/', home, name='home'),
    path('logout/', user_logout, name='logout'),
    path('create_bill/', create_bill, name='create_bill'),
    path('previous_bills/', previous_bills, name='previous_bills'),
]

