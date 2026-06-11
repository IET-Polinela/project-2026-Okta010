from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Count
from main_app.models import Report

# View untuk menampilkan halaman
class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

# View khusus untuk mengirim data JSON
def dashboard_data(request):
    # Agregasi data menggunakan Count
    status_data = Report.objects.values('status').annotate(total=Count('status'))
    category_data = Report.objects.values('category').annotate(total=Count('category'))

    # Mengambil 5 laporan terbaru
    latest_reported = list(Report.objects.filter(status='REPORTED').order_by('-id')[:5].values('title', 'category', 'status'))
    latest_resolved = list(Report.objects.filter(status='RESOLVED').order_by('-id')[:5].values('title', 'category', 'status'))

    return JsonResponse({
        'status_labels': [item['status'] for item in status_data],
        'status_counts': [item['total'] for item in status_data],
        'category_labels': [item['category'] for item in category_data],
        'category_counts': [item['total'] for item in category_data],
        'latest_reported': latest_reported,
        'latest_resolved': latest_resolved,
    })