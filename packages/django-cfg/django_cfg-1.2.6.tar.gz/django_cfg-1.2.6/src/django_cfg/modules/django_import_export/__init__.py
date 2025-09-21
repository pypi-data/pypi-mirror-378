"""
Django Import/Export Integration for Django CFG

Simple re-export of django-import-export components through django-cfg registry.
Provides seamless integration without unnecessary wrappers.
"""

# Re-export original classes through django-cfg registry
from import_export.admin import ImportExportMixin as BaseImportExportMixin, ImportExportModelAdmin as BaseImportExportModelAdmin, ExportMixin as BaseExportMixin, ImportMixin as BaseImportMixin
from import_export.resources import ModelResource as BaseResource
from import_export.forms import ImportForm, ExportForm, SelectableFieldsExportForm


class ImportExportMixin(BaseImportExportMixin):
    """Django-CFG enhanced ImportExportMixin with custom templates."""
    change_list_template = 'admin/import_export/change_list_import_export.html'


class ImportExportModelAdmin(BaseImportExportModelAdmin):
    """Django-CFG enhanced ImportExportModelAdmin with custom templates."""
    change_list_template = 'admin/import_export/change_list_import_export.html'


class ExportMixin(BaseExportMixin):
    """Django-CFG enhanced ExportMixin with custom templates."""
    change_list_template = 'admin/import_export/change_list_export.html'


class ImportMixin(BaseImportMixin):
    """Django-CFG enhanced ImportMixin with custom templates."""
    change_list_template = 'admin/import_export/change_list_import.html'


__all__ = [
    'ImportExportMixin',
    'ImportExportModelAdmin',
    'ExportMixin',
    'ImportMixin',
    'BaseResource',
    'ImportForm',
    'ExportForm',
    'SelectableFieldsExportForm',
]