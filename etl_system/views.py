# etl_system/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import subprocess
import sys
import os
from datetime import date
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

# ETL Execution and Data Loading Views
@login_required
@permission_required('etl_system.view_sourceinfo', raise_exception=True)
def etl_execution(request):
    """View to manage ETL execution"""
    sources = SourceInfo.objects.all()
    return render(request, 'etl_system/ETL_Execution/etl_execution.html', {'sources': sources})

@login_required
@permission_required('etl_system.view_sourceinfo', raise_exception=True)
def execute_etl(request, datasrc_id):
    """Execute ETL for a specific data source"""
    if request.method == 'POST':
        try:
            # Get the path to load_table.py
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'load_table.py')
            
            # Execute the ETL script
            result = subprocess.run([
                sys.executable, script_path, str(datasrc_id)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                messages.success(request, f'ETL execution completed successfully for Data Source ID: {datasrc_id}')
                return JsonResponse({
                    'status': 'success',
                    'message': f'ETL completed for Data Source ID: {datasrc_id}',
                    'output': result.stdout
                })
            else:
                messages.error(request, f'ETL execution failed: {result.stderr}')
                return JsonResponse({
                    'status': 'error',
                    'message': f'ETL failed: {result.stderr}',
                    'output': result.stdout
                })
                
        except subprocess.TimeoutExpired:
            messages.error(request, 'ETL execution timed out')
            return JsonResponse({
                'status': 'error',
                'message': 'ETL execution timed out'
            })
        except Exception as e:
            messages.error(request, f'Error executing ETL: {str(e)}')
            return JsonResponse({
                'status': 'error',
                'message': f'Error executing ETL: {str(e)}'
            })
    
    return redirect('etl_execution')

@login_required
@permission_required('etl_system.view_tableinfo', raise_exception=True)
def data_viewer(request):
    """View to display available tables for data viewing"""
    tables = TableInfo.objects.all()
    return render(request, 'etl_system/Data_Viewer/data_viewer.html', {'tables': tables})

def get_db_engine(db_info):
    """Helper function to create database engine"""
    db_type = db_info['db_type'].lower()
    if db_type == 'postgre':
        conn_str = f"postgresql+psycopg2://{db_info['username1']}:{db_info['password1']}@{db_info['host1']}/{db_info['database1']}"
    elif db_type == 'mysql':
        conn_str = f"mysql+pymysql://{db_info['username1']}:{db_info['password1']}@{db_info['host1']}:{db_info['port1']}/{db_info['database1']}"
    elif db_type == 'mysql_wh':
        conn_str = f"mysql+pymysql://{db_info['username1']}:{db_info['password1']}@{db_info['host1']}/{db_info['database1']}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    return create_engine(conn_str)

@login_required
@permission_required('etl_system.view_tableinfo', raise_exception=True)
def view_table_data(request, table_id):
    """View data from a specific table"""
    try:
        table_info = get_object_or_404(TableInfo, SRCTBL_ID=table_id)
        
        # Get target database credentials
        try:
            db_cred = DatabaseCred.objects.filter(db_type__iexact=table_info.TGT_DATABASE).first()
            if not db_cred:
                messages.error(request, f'No credentials found for database type: {table_info.TGT_DATABASE}')
                return redirect('data_viewer')
            
            # Create database engine
            engine = get_db_engine({
                'db_type': db_cred.db_type,
                'host1': db_cred.host1,
                'port1': db_cred.port1,
                'database1': db_cred.database1,
                'username1': db_cred.username1,
                'password1': db_cred.password1
            })
            
            # Build the full table name
            if table_info.TGT_SCHEMA:
                full_table_name = f"{table_info.TGT_SCHEMA}.{table_info.TGT_TABLENAME}"
            else:
                full_table_name = table_info.TGT_TABLENAME
            
            # Get pagination parameters
            page = request.GET.get('page', 1)
            per_page = int(request.GET.get('per_page', 50))
            search = request.GET.get('search', '')
            
            # Build query
            base_query = f"SELECT * FROM {full_table_name}"
            count_query = f"SELECT COUNT(*) as total FROM {full_table_name}"
            
            # Add search filter if provided
            if search:
                # Get table schema to build search conditions
                schemas = TableSchema.objects.filter(SRCTBL_ID=table_id, SRC_TRG_IND='TRG')
                if schemas.exists():
                    search_conditions = []
                    for schema in schemas:
                        if schema.DATA_TYPE and 'varchar' in schema.DATA_TYPE.lower():
                            search_conditions.append(f"{schema.COLUMN_NM} LIKE '%{search}%'")
                    
                    if search_conditions:
                        where_clause = " OR ".join(search_conditions)
                        base_query += f" WHERE {where_clause}"
                        count_query += f" WHERE {where_clause}"
            
            # Get total count
            with engine.connect() as conn:
                total_count = conn.execute(text(count_query)).fetchone()[0]
            
            # Calculate pagination
            offset = (int(page) - 1) * per_page
            data_query = f"{base_query} LIMIT {per_page} OFFSET {offset}"
            
            # Fetch data
            df = pd.read_sql(data_query, engine)
            
            # Create paginator-like object for template
            total_pages = (total_count + per_page - 1) // per_page
            has_previous = int(page) > 1
            has_next = int(page) < total_pages
            
            pagination_info = {
                'page': int(page),
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_previous': has_previous,
                'has_next': has_next,
                'previous_page': int(page) - 1 if has_previous else None,
                'next_page': int(page) + 1 if has_next else None,
            }
            
            # Convert DataFrame to list of dictionaries for template
            data = df.to_dict('records') if not df.empty else []
            columns = df.columns.tolist() if not df.empty else []
            
            context = {
                'table_info': table_info,
                'data': data,
                'columns': columns,
                'pagination': pagination_info,
                'search': search,
                'per_page': per_page,
            }
            
            return render(request, 'etl_system/Data_Viewer/table_data.html', context)
            
        except Exception as e:
            messages.error(request, f'Error fetching data: {str(e)}')
            return redirect('data_viewer')
            
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('data_viewer')

@login_required
@permission_required('etl_system.view_tableinfo', raise_exception=True)
def export_table_data(request, table_id):
    """Export table data to CSV"""
    try:
        table_info = get_object_or_404(TableInfo, SRCTBL_ID=table_id)
        
        # Get target database credentials
        db_cred = DatabaseCred.objects.filter(db_type__iexact=table_info.TGT_DATABASE).first()
        if not db_cred:
            messages.error(request, f'No credentials found for database type: {table_info.TGT_DATABASE}')
            return redirect('data_viewer')
        
        # Create database engine
        engine = get_db_engine({
            'db_type': db_cred.db_type,
            'host1': db_cred.host1,
            'port1': db_cred.port1,
            'database1': db_cred.database1,
            'username1': db_cred.username1,
            'password1': db_cred.password1
        })
        
        # Build the full table name
        if table_info.TGT_SCHEMA:
            full_table_name = f"{table_info.TGT_SCHEMA}.{table_info.TGT_TABLENAME}"
        else:
            full_table_name = table_info.TGT_TABLENAME
        
        # Fetch all data
        query = f"SELECT * FROM {full_table_name}"
        df = pd.read_sql(query, engine)
        
        # Create HTTP response with CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{table_info.TGT_TABLENAME}_{date.today()}.csv"'
        
        # Write CSV to response
        df.to_csv(path_or_buf=response, index=False)
        
        return response
        
    except Exception as e:
        messages.error(request, f'Error exporting data: {str(e)}')
        return redirect('data_viewer')

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