from django.contrib import admin as admin
from typing import Any

class SiteAdmin(admin.ModelAdmin):
    list_display: Any = ...
    search_fields: Any = ...
