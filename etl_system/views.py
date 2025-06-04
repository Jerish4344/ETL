# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import SourceInfo, TableInfo, SourceFileInfo, TableSchema, DatabaseCred
from .forms import SourceInfoForm, TableInfoForm, SourceFileInfoForm, TableSchemaForm, DatabaseCredForm

# Dashboard View
@login_required
def dashboard(request):
    user = request.user
    is_admin = user.groups.filter(name='ETL_Admin').exists()
    
    context = {
        'is_admin': is_admin,
        'source_info_count': SourceInfo.objects.count(),
        'table_info_count': TableInfo.objects.count(),
        'source_file_count': SourceFileInfo.objects.count(),
        'table_schema_count': TableSchema.objects.count(),
        'database_cred_count': DatabaseCred.objects.count(),
    }
    
    if is_admin:
        context['database_cred_count'] = DatabaseCred.objects.count(),
    
    return render(request, 'etl_system/dashboard.html', context)

# Source Info Views
class SourceInfoListView(LoginRequiredMixin, ListView):
    model = SourceInfo
    template_name = 'etl_system/Sources_Info/source_info_list.html'
    context_object_name = 'sources'

class SourceInfoDetailView(LoginRequiredMixin, DetailView):
    model = SourceInfo
    template_name = 'etl_system/Sources_Info/source_info_detail.html'
    context_object_name = 'source'

class SourceInfoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SourceInfo
    form_class = SourceInfoForm
    template_name = 'etl_system/Sources_Info/source_info_form.html'
    success_url = reverse_lazy('source_info_list')
    permission_required = 'etl_system.add_sourceinfo'

class SourceInfoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SourceInfo
    form_class = SourceInfoForm
    template_name = 'etl_system/Sources_Info/source_info_form.html'
    success_url = reverse_lazy('source_info_list')
    permission_required = 'etl_system.change_sourceinfo'

class SourceInfoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SourceInfo
    template_name = 'etl_system/Sources_Info/source_info_confirm_delete.html'
    success_url = reverse_lazy('source_info_list')
    permission_required = 'etl_system.delete_sourceinfo'

# Table Info Views
class TableInfoListView(LoginRequiredMixin, ListView):
    model = TableInfo
    template_name = 'etl_system/Tables_Info/table_info_list.html'
    context_object_name = 'tables'

class TableInfoDetailView(LoginRequiredMixin, DetailView):
    model = TableInfo
    template_name = 'etl_system/Tables_Info/table_info_detail.html'
    context_object_name = 'table'

class TableInfoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TableInfo
    form_class = TableInfoForm
    template_name = 'etl_system/Tables_Info/table_info_form.html'
    success_url = reverse_lazy('table_info_list')
    permission_required = 'etl_system.add_tableinfo'

class TableInfoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TableInfo
    form_class = TableInfoForm
    template_name = 'etl_system/Tables_Info/table_info_form.html'
    success_url = reverse_lazy('table_info_list')
    permission_required = 'etl_system.change_tableinfo'

class TableInfoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TableInfo
    template_name = 'etl_system/Tables_Info/table_info_confirm_delete.html'
    success_url = reverse_lazy('table_info_list')
    permission_required = 'etl_system.delete_tableinfo'

# Source File Info Views
class SourceFileInfoListView(LoginRequiredMixin, ListView):
    model = SourceFileInfo
    template_name = 'etl_system/Source_File_Info/source_file_info_list.html'
    context_object_name = 'files'

class SourceFileInfoDetailView(LoginRequiredMixin, DetailView):
    model = SourceFileInfo
    template_name = 'etl_system/Source_File_Info/source_file_info_detail.html'
    context_object_name = 'file'

class SourceFileInfoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = SourceFileInfo
    form_class = SourceFileInfoForm
    template_name = 'etl_system/Source_File_Info/source_file_info_form.html'
    success_url = reverse_lazy('source_file_info_list')
    permission_required = 'etl_system.add_sourcefileinfo'

class SourceFileInfoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = SourceFileInfo
    form_class = SourceFileInfoForm
    template_name = 'etl_system/Source_File_Info/source_file_info_form.html'
    success_url = reverse_lazy('source_file_info_list')
    permission_required = 'etl_system.change_sourcefileinfo'

class SourceFileInfoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = SourceFileInfo
    template_name = 'etl_system/Source_File_Info/source_file_info_confirm_delete.html'
    success_url = reverse_lazy('source_file_info_list')
    permission_required = 'etl_system.delete_sourcefileinfo'

# Table Schema Views
class TableSchemaListView(LoginRequiredMixin, ListView):
    model = TableSchema
    template_name = 'etl_system/Table_Schema/table_schema_list.html'
    context_object_name = 'schemas'

class TableSchemaDetailView(LoginRequiredMixin, DetailView):
    model = TableSchema
    template_name = 'etl_system/Table_Schema/table_schema_detail.html'
    context_object_name = 'schema'

class TableSchemaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TableSchema
    form_class = TableSchemaForm
    template_name = 'etl_system/Table_Schema/table_schema_form.html'
    success_url = reverse_lazy('table_schema_list')
    permission_required = 'etl_system.add_tableschema'

class TableSchemaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = TableSchema
    form_class = TableSchemaForm
    template_name = 'etl_system/Table_Schema/table_schema_form.html'
    success_url = reverse_lazy('table_schema_list')
    permission_required = 'etl_system.change_tableschema'

class TableSchemaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = TableSchema
    template_name = 'etl_system/Table_Schema/table_schema_confirm_delete.html'
    success_url = reverse_lazy('table_schema_list')
    permission_required = 'etl_system.delete_tableschema'

# Database Credential Views (Admin Only)
class DatabaseCredListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = DatabaseCred
    template_name = 'etl_system/Database_Info/database_cred_list.html'
    context_object_name = 'credentials'
    permission_required = 'etl_system.view_databasecred'

class DatabaseCredDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = DatabaseCred
    template_name = 'etl_system/Database_Info/database_cred_detail.html'
    context_object_name = 'credential'
    permission_required = 'etl_system.view_databasecred'

class DatabaseCredCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = DatabaseCred
    form_class = DatabaseCredForm
    template_name = 'etl_system/Database_Info/database_cred_form.html'
    success_url = reverse_lazy('database_cred_list')
    permission_required = 'etl_system.add_databasecred'

class DatabaseCredUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = DatabaseCred
    form_class = DatabaseCredForm
    template_name = 'etl_system/Database_Info/database_cred_form.html'
    success_url = reverse_lazy('database_cred_list')
    permission_required = 'etl_system.change_databasecred'

class DatabaseCredDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = DatabaseCred
    template_name = 'etl_system/Database_Info/database_cred_confirm_delete.html'
    success_url = reverse_lazy('database_cred_list')
    permission_required = 'etl_system.delete_databasecred'
