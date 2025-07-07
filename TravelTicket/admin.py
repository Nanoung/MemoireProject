from django.contrib import admin

from TravelTicket.models import Horaire, SegmentVoyage

# Register your models here.
class HoraireAdmin(admin.ModelAdmin):
    time_format = '%H:%M'
    list_display =('id','heuredepart')

class SegmentVoyageAdmin(admin.ModelAdmin):
    list_display =('id','voyage','segment','heuredepart','tarif','plase_disponible')



admin.site.register(Horaire,HoraireAdmin)
admin.site.register(SegmentVoyage,SegmentVoyageAdmin)



