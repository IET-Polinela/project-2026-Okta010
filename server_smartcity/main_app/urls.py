from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'), 
    path('list/', views.ReportListView.as_view(), name='report_list'),
    
    path('add/', views.ReportCreateView.as_view(), name='add_report'),
    
    path('search/', views.search_view, name='report_search'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/data/', views.dashboard_data, name='dashboard_data'),
    path('report/<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    
    path('report/update/<int:pk>/', views.ReportUpdateView.as_view(), name='update_report'),
    path('report/delete/<int:pk>/', views.ReportDeleteView.as_view(), name='delete_report'),
    path('report/update-status/<int:pk>/', views.ReportUpdateStatusView.as_view(), name='update_status'),
]