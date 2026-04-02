from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('add/', views.add_report, name='add_report'),
    path('update/<int:id>/', views.update_report, name='update_report'),
    path('delete/<int:id>/', views.delete_report, name='delete_report'),
    path('verify/<int:id>/', views.verify_report, name='verify_report')
]