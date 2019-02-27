from django.contrib import admin

from .models import File2Exchange


@admin.register(File2Exchange)
class File2ExchangeAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'process', 'step', 'model', 'active')
