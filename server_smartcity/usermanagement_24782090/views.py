from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CitizenRegistrationForm
from .models import User

# View untuk proses Login
class UserLoginView(LoginView):
    template_name = 'login.html'
    def get_success_url(self):
        return reverse_lazy('report_list')

# View untuk proses Logout
class UserLogoutView(LogoutView):
    next_page = 'login'

# View untuk pendaftaran Citizen (Lab 6)
class CitizenRegistrationView(CreateView):
    model = User
    form_class = CitizenRegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')