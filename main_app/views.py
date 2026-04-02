from django.shortcuts import render, redirect, get_object_or_404
from .models import Report
from .forms import ReportForm

# READ
def home(request):
    reports = Report.objects.all()
    return render(request, 'main_app/home.html', {'reports': reports})


# CREATE
def add_report(request):
    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ReportForm()
    return render(request, 'main_app/add_report.html', {'form': form})


# UPDATE
def update_report(request, id):
    report = get_object_or_404(Report, id=id)
    form = ReportForm(request.POST or None, instance=report)
    if form.is_valid():
        form.save()
        return redirect('home')
    return render(request, 'main_app/update_report.html', {'form': form})


# DELETE
def delete_report(request, id):
    report = get_object_or_404(Report, id=id)
    report.delete()
    return redirect('home')


#Verifikasi
def verify_report(request, id):
    report = get_object_or_404(Report, id=id)
    report.status = 'VERIFIED'
    report.save()
    return redirect('home')