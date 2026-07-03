from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import Http404, JsonResponse
from django.db.models import Count
from .models import Report
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib.auth.mixins import UserPassesTestMixin


def home_view(request):
    return render(request, 'main_app/home.html')

@login_required
def search_view(request):
    if not request.user.is_staff:
        raise PermissionDenied 
    return render(request, 'main_app/report_list.html')

def report_create_view(request):
    return redirect('add_report')

def report_detail_api(request, pk):
    try:
        report = Report.objects.get(pk=pk)
        return JsonResponse({'status': 'ok'})
    except Report.DoesNotExist:
        raise Http404("Report not found")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'
    login_url = 'login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

@login_required
def dashboard_data(request):
    status_data = Report.objects.values('status').annotate(total=Count('status'))
    category_data = Report.objects.values('category').annotate(total=Count('category'))
    return JsonResponse({
        'status_labels': [item['status'] for item in status_data],
        'status_counts': [item['total'] for item in status_data],
        'category_labels': [item['category'] for item in category_data],
        'category_counts': [item['total'] for item in category_data],
    })


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'main_app/report_list.html' 
    context_object_name = 'reports'
    ordering = ['-id']
    login_url = 'login'

class ReportDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    login_url = 'login'
    model = Report

    def test_func(self):
        # Admin bisa lihat semua, warga hanya bisa lihat laporannya sendiri
        return self.request.user.is_staff or self.get_object().reporter == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.object
        allowed_transitions = {
            "DRAFT": ["REPORTED"],
            "REPORTED": ["VERIFIED"],
            "VERIFIED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["RESOLVED"],
            "RESOLVED": [],
        }
        context["allowed_transitions"] = allowed_transitions.get(report.status, [])
        
        return context
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            report = self.get_object()
            return JsonResponse({
                'title': report.title, 'category': report.category,
                'location': report.location, 'description': report.description,
                'status': report.status,
            })
        return super().render_to_response(context, **response_kwargs)


class ReportCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil ditambahkan!"

    def test_func(self):
        # Pastikan hanya staff yang bisa membuat laporan (sesuai ekspektasi tes)
        return self.request.user.is_staff
    
    def handle_no_permission(self):
        # Jika bukan staff, lempar error 403 (Forbidden)
        raise PermissionDenied
    
class ReportUpdateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil diperbarui!"

    def test_func(self):
        report = self.get_object()
        # Hanya pemilik laporan saat status DRAFT yang dapat mengubah konten.
        # Admin tidak diberikan izin untuk mengedit isi laporan di portal ini;
        # admin hanya boleh merubah status melalui ReportUpdateStatusView.
        return report.reporter == self.request.user and report.status == 'DRAFT'
    

class ReportDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')

    def test_func(self):
        report = self.get_object()
        # Hanya pemilik laporan saat status DRAFT yang dapat menghapus laporan.
        # Mencegah admin menghapus laporan lewat UI biasa; pengelolaan
        # administratif dilakukan melalui mekanisme terpisah bila diperlukan.
        return report.reporter == self.request.user and report.status == 'DRAFT'

@method_decorator(login_required, name='dispatch')
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        
        # Hanya admin yang bisa update status
        if not request.user.is_staff:
            messages.error(request, "Anda tidak memiliki izin untuk mengubah status laporan.")
            return redirect('report_list')
                
        new_status = (
            request.POST.get("new_status")
            or request.POST.get("status")
        )

        allowed_transitions = {
            "DRAFT": ["REPORTED"],
            "REPORTED": ["VERIFIED"],
            "VERIFIED": ["IN_PROGRESS"],
            "IN_PROGRESS": ["RESOLVED"],
            "RESOLVED": [],
        }

        if (
            new_status
            and new_status in allowed_transitions.get(report.status, [])
        ):
            report.status = new_status
            report.save()
            messages.success(request, "Status laporan berhasil diperbarui!")
        else:
            messages.error(request, "Transisi status tidak diperbolehkan.")

        return redirect("report_detail", pk=report.pk)