from django.urls import path
from .views import DashboardView, dashboard_data

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('api/data/', dashboard_data, name='api_data'),
]