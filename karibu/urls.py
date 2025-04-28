"""
URL configuration for karibu project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
#accessing the views files in our application
from home import views
#
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    #below is the url for index page
    path('',views.index, name='index'),

    #below is the url for stock page
    path('addstock/<str:pk>/',views.addstock, name='addstock'),

    #below is the the url for sales page
    path('addsales/',views.addsales, name='addsales'),

    #below is the url for receipt page
    path('receipt/',views.receipt, name='receipt'),

    #below is the url for all_sales
    path('allstock/',views.all_stock, name='allstock'),

    #below is the url for all_stock
    path('allsales/',views.all_sales, name='allsales'),

    #handling a url for a particular checkout item
    path('home/<int:stock_id>/', views.stock_detail, name='stock_detail'),
    
    #handling a url for a particular sell item
    path('issue_item/<str:pk>/', views.issue_item, name='issue_item'),

    path('receipt/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),

    #('', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),

    path('logout/', auth_views.LogoutView.as_view(template_name='home/logout.html'), name='logout'),

    path('login/', views.Login, name='login'),

    path('signup/', views.signup, name='signup'),

    path('dashboard3/', views.salesagent, name='salesagent'),
    path('dashboard2/', views.manager, name='manager'),
    path('dashboard1/', views.owner, name='owner'),
]
