from django.db import models
from django.contrib.auth.models import User

class DatabaseCred(models.Model):
    db_type = models.CharField(max_length=50)
    db_role = models.CharField(max_length=50)
    host1 = models.CharField(max_length=255)
    port1 = models.IntegerField()
    database1 = models.CharField(max_length=255)
    username1 = models.CharField(max_length=255)
    password1 = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.db_type} - {self.db_role}"
    
    class Meta:
        db_table = 'ETL_DATABASE_CRED'
        verbose_name = 'Database Credential'
        verbose_name_plural = 'Database Credentials'

class SourceInfo(models.Model):
    SOURCE_ID = models.AutoField(primary_key=True)
    SOURCE_NM = models.CharField(max_length=64, null=True, blank=True)
    SOURCE_TYP = models.CharField(max_length=64, null=True, blank=True)
    USERID = models.CharField(max_length=64, null=True, blank=True)
    USERPSWRD = models.CharField(max_length=64, null=True, blank=True)
    EXTRCT_MTHD = models.CharField(max_length=8, null=True, blank=True)
    
    def __str__(self):
        return f"{self.SOURCE_NM}"
    
    class Meta:
        db_table = 'ETL_SOURCE_INFO'
        verbose_name = 'Source Information'
        verbose_name_plural = 'Source Information'

class TableInfo(models.Model):
    SRCTBL_ID = models.AutoField(primary_key=True)
    DATASRC_ID = models.IntegerField()
    SRC_DATABASE = models.CharField(max_length=64, null=True, blank=True)
    SRC_SCHEMA = models.CharField(max_length=64, null=True, blank=True)
    SRC_TABLENAME = models.CharField(max_length=64, null=True, blank=True)
    TGT_DATABASE = models.CharField(max_length=64, null=True, blank=True)
    TGT_SCHEMA = models.CharField(max_length=64, null=True, blank=True)
    TGT_TABLENAME = models.CharField(max_length=64, null=True, blank=True)
    SRCLAYOUT_ID = models.IntegerField()
    TRGLAYOUT_ID = models.IntegerField()
    
    def __str__(self):
        return f"{self.SRC_TABLENAME} -> {self.TGT_TABLENAME}"
    
    class Meta:
        db_table = 'ETL_TABLE_INFO'
        verbose_name = 'Table Information'
        verbose_name_plural = 'Table Information'

class SourceFileInfo(models.Model):
    SRCFILE_ID = models.AutoField(primary_key=True)
    DATASRC_ID = models.IntegerField()
    SRC_DIRECTORY = models.CharField(max_length=255, null=True, blank=True)
    SRC_FILENAME = models.CharField(max_length=255, null=True, blank=True)
    TGT_DATABASE = models.CharField(max_length=64, null=True, blank=True)
    TGT_TABLENAME = models.CharField(max_length=64, null=True, blank=True)
    SRCLAYOUT_ID = models.IntegerField()
    TRGLAYOUT_ID = models.IntegerField()
    
    def __str__(self):
        return f"{self.SRC_FILENAME}"
    
    class Meta:
        db_table = 'ETL_SRCFILE_INFO'
        verbose_name = 'Source File Information'
        verbose_name_plural = 'Source File Information'

class TableSchema(models.Model):
    SRCTBL_ID = models.IntegerField(primary_key=True)
    COLUMN_SEQ = models.IntegerField()
    SRC_TRG_IND = models.CharField(max_length=3)
    SCHEMA_NM = models.CharField(max_length=64, null=True, blank=True)
    TABLE_NM = models.CharField(max_length=64, null=True, blank=True)
    COLUMN_NM = models.CharField(max_length=64, null=True, blank=True)
    DATA_TYPE = models.CharField(max_length=64, null=True, blank=True)
    XFRMTN = models.CharField(max_length=128, null=True, blank=True)
    PRIMARY_KEY = models.CharField(max_length=1, null=True, blank=True)
    DEFAULT_VAL = models.CharField(max_length=64, null=True, blank=True)
    
    def __str__(self):
        return f"{self.TABLE_NM}.{self.COLUMN_NM}"
    
    class Meta:
        db_table = 'ETL_TBL_SCHEMA'
        verbose_name = 'Table Schema'
        verbose_name_plural = 'Table Schemas'
        unique_together = (('SRCTBL_ID', 'COLUMN_SEQ', 'SRC_TRG_IND'),)