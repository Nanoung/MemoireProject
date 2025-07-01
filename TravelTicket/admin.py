from django.contrib import admin

from TravelTicket.models import Horaire

# Register your models here.
class HoraireAdmin(admin.ModelAdmin):
    time_format = '%H:%M'
    list_display =('id','heuredepart')


admin.site.register(Horaire,HoraireAdmin)
