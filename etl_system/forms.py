from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import SourceInfo, TableInfo, SourceFileInfo, TableSchema, DatabaseCred

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

class SourceInfoForm(forms.ModelForm):
    class Meta:
        model = SourceInfo
        fields = '__all__'
        widgets = {
            'SOURCE_NM': forms.TextInput(attrs={'class': 'form-control'}),
            'SOURCE_TYP': forms.TextInput(attrs={'class': 'form-control'}),
            'USERID': forms.TextInput(attrs={'class': 'form-control'}),
            'USERPSWRD': forms.PasswordInput(attrs={'class': 'form-control'}),
            'EXTRCT_MTHD': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TableInfoForm(forms.ModelForm):
    class Meta:
        model = TableInfo
        fields = '__all__'
        widgets = {
            'DATASRC_ID': forms.NumberInput(attrs={'class': 'form-control'}),
            'SRC_DATABASE': forms.TextInput(attrs={'class': 'form-control'}),
            'SRC_SCHEMA': forms.TextInput(attrs={'class': 'form-control'}),
            'SRC_TABLENAME': forms.TextInput(attrs={'class': 'form-control'}),
            'TGT_DATABASE': forms.TextInput(attrs={'class': 'form-control'}),
            'TGT_SCHEMA': forms.TextInput(attrs={'class': 'form-control'}),
            'TGT_TABLENAME': forms.TextInput(attrs={'class': 'form-control'}),
            'SRCLAYOUT_ID': forms.NumberInput(attrs={'class': 'form-control'}),
            'TRGLAYOUT_ID': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SourceFileInfoForm(forms.ModelForm):
    class Meta:
        model = SourceFileInfo
        fields = '__all__'
        widgets = {
            'DATASRC_ID': forms.NumberInput(attrs={'class': 'form-control'}),
            'SRC_DIRECTORY': forms.TextInput(attrs={'class': 'form-control'}),
            'SRC_FILENAME': forms.TextInput(attrs={'class': 'form-control'}),
            'TGT_DATABASE': forms.TextInput(attrs={'class': 'form-control'}),
            'TGT_TABLENAME': forms.TextInput(attrs={'class': 'form-control'}),
            'SRCLAYOUT_ID': forms.NumberInput(attrs={'class': 'form-control'}),
            'TRGLAYOUT_ID': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class TableSchemaForm(forms.ModelForm):
    class Meta:
        model = TableSchema
        fields = '__all__'
        widgets = {
            'SRCTBL_ID': forms.NumberInput(attrs={'class': 'form-control'}),
            'COLUMN_SEQ': forms.NumberInput(attrs={'class': 'form-control'}),
            'SRC_TRG_IND': forms.TextInput(attrs={'class': 'form-control'}),
            'SCHEMA_NM': forms.TextInput(attrs={'class': 'form-control'}),
            'TABLE_NM': forms.TextInput(attrs={'class': 'form-control'}),
            'COLUMN_NM': forms.TextInput(attrs={'class': 'form-control'}),
            'DATA_TYPE': forms.TextInput(attrs={'class': 'form-control'}),
            'XFRMTN': forms.TextInput(attrs={'class': 'form-control'}),
            'PRIMARY_KEY': forms.TextInput(attrs={'class': 'form-control'}),
            'DEFAULT_VAL': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DatabaseCredForm(forms.ModelForm):
    class Meta:
        model = DatabaseCred
        fields = '__all__'
        widgets = {
            'db_type': forms.TextInput(attrs={'class': 'form-control'}),
            'db_role': forms.TextInput(attrs={'class': 'form-control'}),
            'host1': forms.TextInput(attrs={'class': 'form-control'}),
            'port1': forms.NumberInput(attrs={'class': 'form-control'}),
            'database1': forms.TextInput(attrs={'class': 'form-control'}),
            'username1': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
        }