import django_filters
from datetime import datetime

class PDFFile:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.date_modified = datetime.fromtimestamp(path.stat().st_mtime)  # Usa .stat() para mayor compatibilidad

class PDFFileFilter(django_filters.FilterSet):
    date_modified = django_filters.DateFilter(method='filter_by_date')

    def filter_by_date(self, queryset, name, value):
        return [pdf for pdf in queryset if pdf.date_modified.date() == value]

    class Meta:
        fields = ['date_modified']
