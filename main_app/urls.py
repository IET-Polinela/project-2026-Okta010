from django.urls import path
from .views import (
    ReportListView, ReportDetailView, ReportCreateView, 
    ReportUpdateView, ReportDeleteView, ReportUpdateStatusView
)

urlpatterns = [
    path('', ReportListView.as_view(), name='home'),
    path('report/<int:pk>/', ReportDetailView.as_view(), name='report_detail'),
    path('report/add/', ReportCreateView.as_view(), name='add_report'),
    path('report/<int:pk>/edit/', ReportUpdateView.as_view(), name='update_report'),
    path('report/<int:pk>/delete/', ReportDeleteView.as_view(), name='delete_report'),
    
    # Routing khusus untuk aksi perubahan status workflow [cite: 190]
    path('report/<int:pk>/update-status/', ReportUpdateStatusView.as_view(), name='update_status'),
]