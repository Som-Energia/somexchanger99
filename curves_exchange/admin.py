from django.contrib import admin

from .models import ProviderConnection, Curve2Exchange


@admin.register(Curve2Exchange)
class Curve2ExchangeAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'name', 'active')


class Curve2ExchangeInline(admin.TabularInline):
    model = Curve2Exchange
    extra = 0


@admin.register(ProviderConnection)
class ProviderConnectionAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'name', 'active')

    fieldsets = [
        (None, {'fields': ['name', 'active']}),
        ('Connection info', {
            'fields': ['host', 'port', 'username', 'password', 'base_dir', 'secure'],
            'classes': ['collapse']
        }),
    ]

    inlines = [Curve2ExchangeInline]
