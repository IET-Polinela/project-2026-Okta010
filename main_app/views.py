from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .models import Report

# a. Menampilkan daftar laporan (ListView) - BISA DIAKSES SEMUA
class ReportListView(ListView):
    model = Report
    template_name = 'main_app/report_list.html' 
    context_object_name = 'reports'
    ordering = ['-id']

# b. Menampilkan detail data laporan (DetailView) - BISA DIAKSES SEMUA
class ReportDetailView(DetailView):
    model = Report
    template_name = 'main_app/report_detail.html'
    context_object_name = 'report'

# c. Pembuatan data laporan baru (CreateView) - KHUSUS ADMIN
class ReportCreateView(SuccessMessageMixin, CreateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan baru berhasil ditambahkan!"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak karena bukan admin")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

# d. Edit data laporan (UpdateView) - KHUSUS ADMIN
class ReportUpdateView(SuccessMessageMixin, UpdateView):
    model = Report
    fields = ['title', 'category', 'description', 'location']
    template_name = 'main_app/add_report.html'
    success_url = reverse_lazy('report_list')
    success_message = "Data laporan berhasil diperbarui!"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak karena bukan admin")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

# e. Penghapusan data laporan (DeleteView) - KHUSUS ADMIN
class ReportDeleteView(SuccessMessageMixin, DeleteView):
    model = Report
    template_name = 'main_app/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')
    success_message = "Laporan berhasil dihapus!"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak karena bukan admin")
            return redirect('report_list')
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(request, *args, **kwargs)

# View khusus untuk workflow perubahan status - KHUSUS ADMIN
class ReportUpdateStatusView(View):
    def post(self, request, pk):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "Akses ditolak")
            return redirect('report_list')
            
        report = get_object_or_404(Report, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status:
            report.status = new_status
            report.save()
            messages.success(request, f"Status laporan berhasil diubah menjadi {new_status}!")
            
        return redirect('report_list')