from django.urls import path
from .views import (
    ReportListView, ReportDetailView, ReportCreateView, 
    ReportUpdateView, ReportDeleteView, ReportUpdateStatusView,
    DashboardView, dashboard_data
)

urlpatterns = [
    path('', ReportListView.as_view(), name='report_list'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('dashboard/data/', dashboard_data, name='dashboard_data'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('report/add/', ReportCreateView.as_view(), name='report_create'),
    path('report/<int:pk>/edit/', ReportUpdateView.as_view(), name='update_report'),
    path('report/<int:pk>/delete/', ReportDeleteView.as_view(), name='delete_report'),
    path('report/status/<int:pk>/', ReportUpdateStatusView.as_view(), name='update_status'),
]