from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Menampilkan kolom is_admin dan is_member di daftar user
    list_display = ('username', 'email', 'is_admin', 'is_member', 'is_staff')
    
    # Menambahkan field kustom ke dalam form edit user di admin panel
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('is_admin', 'is_member')}),
    )
    
    # Menambahkan field kustom saat membuat user baru lewat admin panel
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('is_admin', 'is_member')}),
    )

# Daftarkan model User dengan konfigurasi CustomUserAdmin
admin.site.register(User, CustomUserAdmin)