from django.contrib import admin
from django.utils.translation import ngettext, ugettext_lazy as _
from .models import Atr2Exchange, Curve2Exchange, File2Exchange, OriginFile


def make_active(modeladmin, request, queryset):
    objects_updated = queryset.update(active=True)
    msg = ngettext(
        '%(count)d %(name)s was marked as active.',
        '%(count)d %(plural_name)s were marked as active.',
        objects_updated
    ) % {
        'count': objects_updated,
        'name': modeladmin.model._meta.verbose_name,
        'plural_name': modeladmin.model._meta.verbose_name_plural
    }
    modeladmin.message_user(request, msg)

make_active.short_description = _('Mark selected objects as active')


def make_inactive(modeladmin, request, queryset):
    objects_updated = queryset.update(active=False)
    msg = ngettext(
        '%(count)d %(name)s was marked as inactive.',
        '%(count)d %(plural_name)s were marked as inactive.',
        objects_updated
    ) % {
        'count': objects_updated,
        'name': modeladmin.model._meta.verbose_name,
        'plural_name': modeladmin.model._meta.verbose_name_plural
    }
    modeladmin.message_user(request, msg)

make_inactive.short_description = _('Mark selected objects as inactive')


@admin.register(Atr2Exchange)
class Atr2ExchangeAdmin(admin.ModelAdmin):
    actions = [make_active, make_inactive,]
    list_display = ('__str__', 'process', 'step', 'model', 'active')
    search_fields = ['process', 'step', 'model',]


@admin.register(Curve2Exchange)
class Curve2ExchangeAdmin(admin.ModelAdmin):
    actions = [make_active, make_inactive,]
    list_display = ('__str__', 'name', 'last_upload', 'active')
    search_fields = ['name',]


@admin.register(File2Exchange)
class File2ExchangeAdmin(admin.ModelAdmin):
    actions = [make_active, make_inactive,]
    list_display = ('__str__', 'name', 'origin', 'pattern', 'active')
    search_fields = ['name', 'origin__name', 'origin__code_name', 'pattern',]


@admin.register(OriginFile)
class OriginAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'name', 'code_name',)
    search_fields = ['name', 'code_name',]
