from django.contrib import admin

from .models import Curve2Exchange, Atr2Exchange


@admin.register(Atr2Exchange)
class File2ExchangeAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'process', 'step', 'model', 'active')


@admin.register(Curve2Exchange)
class Curve2ExchangeAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'name', 'active')
