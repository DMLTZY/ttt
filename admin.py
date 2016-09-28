from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import OfficeSupplies, Category, MyUser, Histroy
from .forms import MyUserCreationForm, MyUserChangeForm


class OfficeSuppliesAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']

    class Meta:
        model = OfficeSupplies


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']

    class Meta:
        model = Category  # OfficeSupplies?


class MyUserAdmin(UserAdmin):
    add_form = MyUserCreationForm
    form = MyUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'mobile')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'mobile', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'mobile', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)


class HistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'supply', 'count', 'status', 'createtime']
    list_display_links = ['user']
    search_fields = ['user']
    ordering = ['user']

    class Meta:
        model = Histroy  # OfficeSupplies?


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(OfficeSupplies, OfficeSuppliesAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Histroy, HistoryAdmin)
