from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.db.models import Count
from .models import Report

class DashboardView(TemplateView):
    template_name = 'dashboard/index.html'

def dashboard_data(request):
    status_data = Report.objects.values('status').annotate(total=Count('status'))
    category_data = Report.objects.values('category').annotate(total=Count('category'))
    return JsonResponse({
        'status_labels': [item['status'] for item in status_data],
        'status_counts': [item['total'] for item in status_data],
        'category_labels': [item['category'] for item in category_data],
        'category_counts': [item['total'] for item in category_data],
    })

class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html' 
    context_object_name = 'reports'
    ordering = ['-id']

class ReportDetailView(DetailView):
    model = Report
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            report = self.get_object()
            data = {
                'title': report.title,
                'category': report.category,
                'location': report.location,
                'description': report.description,
                'status': report.status,
            }
            return JsonResponse(data)
        return super().render_to_response(context, **response_kwargs)

class ReportCreateView(SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil ditambahkan!"

class ReportUpdateView(SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil diperbarui!"

class ReportDeleteView(DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')

class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        if new_status:
            report.status = new_status
            report.save()
        return redirect('report_list')