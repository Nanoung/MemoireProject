"""
URL configuration for MemoireProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from MemoireProject import settings
from TravelTicket import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('TravelTicket/admin/ville/', views.ville, name='ville'),
    # path('TravelTicket/admin/ville/add/', views.ville_add, name='ville-add'),
    path('TravelTicket/admin/ville/edit/<int:id>/', views.ville_edit, name='ville_edit'),
    path('TravelTicket/admin/ville/delete/<int:id>/', views.ville_delete, name='ville_delete'),
    path('TravelTicket/admin/typecar/', views.typecar, name='typecar'),
    path('TravelTicket/admin/typecar/edit/<int:id>/', views.typecar_edit, name='typecar_edit'),
    path('TravelTicket/admin/typecar/delete/<int:id>/', views.typecar_delete, name='typecar_delete'),

    path('TravelTicket/admin/avantage/', views.avantage, name='avantage'),
    # path('TravelTicket/admin/avantage/', views.avantage, name='avantage'),
    # path('TravelTicket/admin/avantage/', views.avantage, name='avantage'),

    path('TravelTicket/admin/conducteur/', views.conducteur, name='conducteur'),
    path('TravelTicket/admin/conducteur/edit/<int:id>/', views.conducteur_edit, name='conducteur_edit'),
    path('TravelTicket/admin/conducteur/delete/<int:id>/', views.conducteur_delete, name='conducteur_delete'),

    path('TravelTicket/admin/car/', views.car, name='car'),
    path('TravelTicket/admin/car/edit/<int:id>/', views.car_edit, name='car_edit'),
    path('TravelTicket/admin/car/delete/<int:id>/', views.car_delete, name='car_delete'),

    path('TravelTicket/admin/gare/', views.gare, name='gare'),
    path('TravelTicket/admin/gare/edit/<int:id>/', views.gare_edit, name='gare_edit'),
    path('TravelTicket/admin/gare/delete/<int:id>/', views.gare_delete, name='gare_delete'),

    path('TravelTicket/admin/ligne/', views.ligne, name='ligne'),
    path('TravelTicket/admin/ligne/edit/<int:id>/', views.ligne_edit, name='ligne_edit'),
    path('TravelTicket/admin/ligne/delete/<int:id>/', views.ligne_delete, name='ligne_delete'),

    path('TravelTicket/admin/assigneconducteur/<int:id>/', views.assigneconducteur, name='assigneconducteur'),
    path('TravelTicket/admin/desassigneconducteur/<int:id>/', views.desassigneconducteur, name='desassigneconducteur'),

    path('TravelTicket/admin/segment/', views.segment, name='segment'),
    path('TravelTicket/admin/segment/edit/<int:id>/', views.segment_edit, name='segment_edit'),
    path('TravelTicket/admin/segment/delete/<int:id>/', views.segment_delete, name='segment_delete'),

    path('TravelTicket/admin/tarifs/', views.tarif_management, name='tarif_management'),
    path('load-typecar-fields/', views.load_tarif_fields, name='load_typecar_fields'),

    path('TravelTicket/admin/segmenttarif/edit/<int:id>/', views.segmenttarif_edit, name='segmenttarif_edit'),
    path('TravelTicket/admin/segmenttarif/delete/<int:id>/', views.segmenttarif_delete, name='segmenttarif_delete'),

    path('TravelTicket/admin/planning/', views.planning, name='planning'),
    path('TravelTicket/admin/planning_edit/edit/<int:id>/', views.planning_edit, name='planning_edit'),
    path('TravelTicket/admin/planning/delete/<int:id>/', views.planning_delete, name='planning_delete'),
    path('TravelTicket/admin/planning/voyage/view/<int:id>/', views.voyage_planning, name='voyage_planning'),

    path('TravelTicket/admin/Voyage/Assignation_Ressource/<int:id>/', views.assignation_ressource, name='assignation_ressource'),
    path('ajax/conducteurs_Car_selectionne/', views.get_conducteurs_by_car, name='get_conducteurs_by_car'),
    path('voyage/admin/<int:id>/changer-statut/', views.changer_statut_voyage, name='changer_statut_voyage'),






]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
