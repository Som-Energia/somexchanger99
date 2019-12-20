from django.contrib import admin

from .models import Atr2Exchange, Curve2Exchange, File2Exchange, OriginFile


@admin.register(Atr2Exchange)
class Atr2ExchangeAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'process', 'step', 'model', 'active')


@admin.register(Curve2Exchange)
class Curve2ExchangeAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'name', 'active')


@admin.register(File2Exchange)
class File2ExchangeAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'name', 'origin', 'pattern', 'active')


@admin.register(OriginFile)
class OriginAdmin(admin.ModelAdmin):
    pass
