from django.urls import path
from .views import (
    ReportListView, ReportDetailView, ReportCreateView, 
    ReportUpdateView, ReportDeleteView, ReportUpdateStatusView,
)

urlpatterns = [
    path('', ReportListView.as_view(), name='report_list'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('report/add/', ReportCreateView.as_view(), name='report_create'),
    path('report/<int:pk>/edit/', ReportUpdateView.as_view(), name='update_report'),
    path('report/<int:pk>/delete/', ReportDeleteView.as_view(), name='delete_report'),
    path('report/status/<int:pk>/', ReportUpdateStatusView.as_view(), name='update_status'),
]