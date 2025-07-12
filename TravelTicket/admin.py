from django.contrib import admin

from TravelTicket.models import Horaire, Remise, Reservation, SegmentVoyage

# Register your models here.
class HoraireAdmin(admin.ModelAdmin):
    time_format = '%H:%M'
    list_display =('id','heuredepart')

class SegmentVoyageAdmin(admin.ModelAdmin):
    list_display =('id','voyage','segment','heuredepart','tarif','plase_disponible')

class ReservationAdmin(admin.ModelAdmin):
    list_display =('id','segmentvoyage','client','panier_code','passager','statut','montant_a_payer','places_reservees','montant_reservation')

class RemiseAdmin(admin.ModelAdmin):
    list_display =('id','libele','montant')


admin.site.register(Horaire,HoraireAdmin)
admin.site.register(SegmentVoyage,SegmentVoyageAdmin)
admin.site.register(Reservation,ReservationAdmin)
admin.site.register(Remise,RemiseAdmin)





