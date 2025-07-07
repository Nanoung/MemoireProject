import base64
from datetime import date, timedelta
import datetime
from pyexpat.errors import messages
from django.forms import modelformset_factory
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import requests

from TravelTicket.models import Car, Conducteur, Gare, Image, Ligne, Passager, Programme, Reservation, Segment, SegmentTypeCar, SegmentVoyage, TypeCar, Ville, Voyage
from TravelTicket.forms import AssignConducteurForm, AssignationForm, AvantageCarForm, CarForm, CityForm, ConducteurForm, DestinationForm, GareForm, LigneForm, PassagerForm, PlanningForm, SegmentForm, SegmentTarifEditForm, SegmentTarifForm, TrajetHoraireForm, TypeCarForm
from geopy.geocoders import Nominatim
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils.timezone import now
from datetime import datetime, timedelta




# Create your views here.
def home(request):
    form=TrajetHoraireForm()
    return render(request, 'TravelTicket/voyage/home.html', {'form':form})

def ville(request):
    villes = Ville.objects.all()
    form = CityForm()
    id_edit = request.POST.get('id_edit') if request.method == 'POST' else None

    if request.method == 'POST':
        if id_edit:  # si modification
            ville_obj = get_object_or_404(Ville, id=id_edit)
            form = CityForm(request.POST)
            if form.is_valid():
                ville_obj.nom = form.cleaned_data['nom']
                ville_obj.region = form.cleaned_data['region']
                geolocator = Nominatim(user_agent="TravelTicket")
                locations = geolocator.geocode(f"{ville_obj.nom}")
                if locations is None:
                    ville_obj.save()
                    return redirect('ville')
                ville_obj.longitude = locations.longitude
                ville_obj.latitude = locations.latitude
                
                ville_obj.save()
                return redirect('ville')  # ou ton nom d’URL
        else:  # sinon création
            form = CityForm(request.POST)
            if form.is_valid():
                geolocator = Nominatim(user_agent="TravelTicket")

                location = geolocator.geocode(f"{form.cleaned_data['nom']}")

                if location is None:
                    Ville.objects.create(
                    nom=form.cleaned_data['nom'],
                    region=form.cleaned_data['region'],
                    longitude=None,
                    latitude=None
                )
                

                Ville.objects.create(
                    nom=form.cleaned_data['nom'],
                    region=form.cleaned_data['region'],
                    longitude=location.longitude,
                    latitude=location.latitude
                )
                return redirect('ville')

    context = {
        'form': form,
        'villes': villes,
        'id_edit': id_edit  # pour savoir dans le template si on est en mode modif
    }

    return render(request, 'TravelTicket/admin/pages/ville.html', context)


def ville_edit(request, id):
    ville_obj = get_object_or_404(Ville, id=id)
    

    # Pré-remplir les champs du formulaire
    form = CityForm(initial={
        'nom': ville_obj.nom,
        'region': ville_obj.region
    })

    villes = Ville.objects.all()  # Pour réafficher la liste aussi

    return render(request, 'TravelTicket/admin/pages/ville.html', {
        'form': form,
        'villes': villes,
        'id_edit': id  # Pour éventuellement cibler en JS
    })

# def ville_edits(request, id):

#     ville_obj = get_object_or_404(Ville, id=id)
#     if request.method == 'POST':
#         form = CityForm(request.POST, instance=ville_obj)
#         if form.is_valid():
#             form.save()
#             return redirect('ville')
#     else:
#         form = CityForm(instance=ville_obj)
#     return render(request, 'TravelTicket/admin/pages/ville.html', {'form': form, 'ville': ville})

def ville_delete(request, id):
    ville = get_object_or_404(Ville, id=id)
    ville.delete()
    return redirect('ville')



def typecar(request):
    typecar=TypeCar.objects.all()
    form = TypeCarForm(request.POST or None)
    formtype = AvantageCarForm()
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        form.save()
        return redirect('typecar')  # Remplace par ta route cible
    return render(request, 'TravelTicket/admin/pages/typeCars.html', {'form': form, 'formtype': formtype, 'typecar': typecar})

def typecar_edit(request, id):
    typecar_edit = TypeCar.objects.get(pk=id)
    print("bien jouer ICI")
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = TypeCarForm(request.POST, instance=typecar_edit)
        print("bien jouerddf ICI")

        if form.is_valid():
            print("bien jouer")
            form.save()
            return redirect('typecar') 
    else:
        form = TypeCarForm(instance=typecar_edit)  
    typecar = TypeCar.objects.all()

    return render(request, 'TravelTicket/admin/pages/typeCars.html', {'form': form,'id_edit': id, 'typecar': typecar})

def typecar_delete(request, id):
    typecar = get_object_or_404(TypeCar, id=id)
    typecar.delete()
    return redirect('typecar')



def avantage(request):
    formtype = AvantageCarForm(request.POST or None)
    if request.method == 'POST' and formtype.is_valid():
        formtype.save()
        return redirect('typecar')  # Remplace par ta route cible
    return render(request, 'TravelTicket/admin/pages/typeCars.html', {'formtype': formtype})






# @csrf_exempt  # Temporaire pour le débogage (à retirer en production)


def conducteur(request):
    # Configuration Traccar
    TRACCAR_SERVER ="https://b649-160-154-230-120.ngrok-free.app" 
    API_USER = "admin"
    API_PASSWORD = "admin"  
    
    form = ConducteurForm(request.POST or None, request.FILES or None)
    conducteurs = Conducteur.objects.all()
    print("bien jouer propor okok")

    if request.method == 'POST' and form.is_valid():
        try:
            auth_basic = base64.b64encode(f"{API_USER}:{API_PASSWORD}".encode()).decode()
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Basic {auth_basic}',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            }
            
            data = f"email={API_USER}&password={API_PASSWORD}"
            
            # Debug avant envoi
            print("=== REQUEST DEBUG ===")
            print("URL:", f"{TRACCAR_SERVER}/api/session")
            print("Headers:", headers)
            print("Body:", data)
            
            session = requests.Session()
            login_response = session.post(
                f"{TRACCAR_SERVER}/api/session",
                headers=headers,
                data=data,  # Important: utiliser data= et non json=
                timeout=15
            )
            
            # Debug réponse
            print("=== RESPONSE DEBUG ===")
            print("Status Code:", login_response.status_code)
            print("Response:", login_response.text)
            
            if login_response.status_code != 200:
                raise Exception(f"Erreur Traccar (HTTP {login_response.status_code}): {login_response.text}")

            # 2. Création de l'appareil (identique à précédemment)
            conducteur = form.save()
            device_data = {
                "name": f"{conducteur.nom} {conducteur.prenom}",
                "uniqueId": f"DRV{conducteur.id}",              
                "category": "car",
                "phone": conducteur.contact
            }
            
            device_response = session.post(
                f"{TRACCAR_SERVER}/api/devices",
                json=device_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            if device_response.status_code == 200:
                conducteur.traccar_device_id = device_response.json().get("id")
                # messages.success(request, "Conducteur et appareil créés avec succès!")
            else:
                raise Exception(f"Erreur création appareil: {device_response.text}")
            
            conducteur.save()
            messages.success(request, "Conducteur ajouté avec succès !")

            return redirect('conducteur')

        except Exception as e:
            print("ERREUR COMPLÈTE:", str(e))
            messages.error(request, f"Erreur technique: {str(e)}")
            form.save()
            return redirect('conducteur')

    return render(request, 'TravelTicket/admin/pages/conducteur.html', {
        'form': form,
        'conducteurs': conducteurs
    })

def conducteur_edit(request, id):
    conducteur_edit = Conducteur.objects.get(pk=id)
    # print("car",conducteur_edit.car)

    print("bien jouer ICI", conducteur_edit)
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = ConducteurForm(request.POST, instance=conducteur_edit)
        print("bien jouerddf ICI")

        if form.is_valid():
            print("bien jouer")
            form.save()
            return redirect('conducteur') 
    else:
        form = ConducteurForm(instance=conducteur_edit)  
        print("form", form)
    conducteurs = Conducteur.objects.all()

    return render(request, 'TravelTicket/admin/pages/conducteur.html', {'form': form,'id_edit': id, 'conducteurs': conducteurs})


def conducteur_delete(request, id):
    TRACCAR_SERVER ="https://b649-160-154-230-120.ngrok-free.app"
    API_USER = "admin"
    API_PASSWORD = "admin"
    conducteur = get_object_or_404(Conducteur, id=id)
    search_response_position = requests.get(
        f"{TRACCAR_SERVER}/api/devices?uniqueId=Nanou20",
        headers={'Authorization': 'Basic ' + base64.b64encode(f"{API_USER}:{API_PASSWORD}".encode()).decode()}
        )
    # print( "search_response_position",search_response_position.json())

    # 1. Récupérer le positionId depuis la réponse de l'appareil
    # position_id = search_response_position.json()[0].get("positionId")
    # print( "position_id",position_id)

    # 2. Requête pour obtenir les détails de la position

    # position_response = requests.get(
    #     f"{TRACCAR_SERVER}/api/positions?id={position_id}",
    #     headers={
    #         "Authorization": "Basic " + base64.b64encode(f"{API_USER}:{API_PASSWORD}".encode()).decode()
    #     }
    # )
    # conducteur.delete()
    if conducteur.delete():
        search_response = requests.get(
        f"{TRACCAR_SERVER}/api/devices?uniqueId=DRV{id}",
        headers={'Authorization': 'Basic ' + base64.b64encode(f"{API_USER}:{API_PASSWORD}".encode()).decode()}
        )
        print(search_response.json())

        if search_response.status_code == 200 and search_response.json():
            device_id = search_response.json()[0].get("id")
            requests.delete(f"{TRACCAR_SERVER}/api/devices/{device_id}", headers={'Authorization': 'Basic ' + base64.b64encode(f"{API_USER}:{API_PASSWORD}".encode()).decode()})
            # Puis supprimer avec l'ID trouvé...
    
    return redirect('conducteur')



def car(request):
    assignerForm = AssignConducteurForm()
    conducteurs_nonassignes = Conducteur.objects.filter(car__isnull=True)
    cars=Car.objects.all()
    form = CarForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        form.save()
        return redirect('car')  # Remplace par ta route cible
    return render(request, 'TravelTicket/admin/pages/Cars.html', {'form': form,'cars': cars, 'assignerForm': assignerForm, 'conducteurs_nonassignes': conducteurs_nonassignes})


def car_edit(request, id):
    car_edit = Car.objects.get(pk=id)
    # print("car",conducteur_edit.car)

    print("bien jouer ICI", car_edit)
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = CarForm(request.POST, instance=car_edit)
        print("bien jouerddf ICI")

        if form.is_valid():
            print("bien jouer")
            form.save()
            return redirect('car') 
    else:
        form = CarForm(instance=car_edit)  
        print("form", form)
    cars = Car.objects.all()

    return render(request, 'TravelTicket/admin/pages/cars.html', {'form': form,'id_edit': id, 'cars': cars})



def car_delete(request, id):
    car = get_object_or_404(Car, id=id)
    car.delete()
    return redirect('car')



def gare(request):
    gares=Gare.objects.all() 

    if request.method == 'POST':

        form = GareForm(request.POST)
        files = request.FILES.getlist('images_upload')  # plusieurs fichiers
        print("files", files)

        if form.is_valid():
            # Initialiser le geolocator
            geolocator = Nominatim(user_agent="TravelTicket")
            
            # Construire l'adresse complète
            nom = form.cleaned_data['nom']
            adresse = form.cleaned_data['adresse']
            ville = form.cleaned_data['ville']
            full_address = f"{adresse}, {ville}"

            try:
                location = geolocator.geocode(full_address)

                # Sauvegarde de l'objet Gare sans commit pour ajouter latitude et longitude
                gare = form.save(commit=False)

                if location:
                    gare.latitude = location.latitude
                    gare.longitude = location.longitude
                else:
                    gare.latitude = None
                    gare.longitude = None
                
                gare.save()
                return redirect('gare')  # ou autre page de redirection
            except Exception as e:
                form.add_error(None, "Erreur lors de la géolocalisation : " + str(e))

            return redirect('gare')  

    else:
        form = GareForm()

    return render(request, 'TravelTicket/admin/pages/gare.html', {'form': form,'gares': gares})


def gare_edit(request, id):
    gare_edit = Gare.objects.get(pk=id)
    images=Image.objects.filter(gare=gare_edit)
    print("images", images) 
    # print("car",conducteur_edit.car)

    print("bien jouer ICI", gare_edit)
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = GareForm(request.POST, instance=gare_edit)
        files = request.FILES.getlist('images')  # Pour les nouvelles images
        
        filess = request.FILES.getlist('images_upload')
        images_to_delete_ids = request.POST.getlist('delete_images')
        if images_to_delete_ids:
            for image_id in images_to_delete_ids:
                Image.objects.filter(id=image_id).delete()


        print("bien jouerddf ICI")

        if form.is_valid():
            print("bien jouer")
            gare=form.save()
            for file in files :
                Image.objects.create(gare=gare, image=file)
            for file in filess:
                Image.objects.create(gare=gare, image=file)

            if images_to_delete_ids:
                for image_id in images_to_delete_ids:
                    Image.objects.filter(id=image_id).delete()
            return redirect('gare') 
            
    else:
        form = GareForm(instance=gare_edit)  
        print("form", form)
    gares = Gare.objects.all()

    return render(request, 'TravelTicket/admin/pages/gare.html', {'form': form,'id_edit': id, 'gares': gares, 'images': images})


def gare_delete(request, id):
    gare = get_object_or_404(Gare, id=id)
    gare.delete()
    return redirect('gare')



def ligne(request):
    lignes=Ligne.objects.all()
    print("lignes", lignes)
    form = LigneForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        form.save()
        return redirect('ligne')  # Remplace par ta route cible
    return render(request, 'TravelTicket/admin/pages/ligne.html', {'form': form,'lignes': lignes})


def ligne_edit(request, id):
    ligne_edit = Ligne.objects.get(pk=id)
    # print("car",conducteur_edit.car)

    print("bien jouer ICI", ligne_edit)
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = LigneForm(request.POST, instance=ligne_edit)
        print("bien jouerddf ICI")

        if form.is_valid():
            print("bien jouer")
            form.save()
            return redirect('ligne') 
    else:
        form = LigneForm(instance=ligne_edit)  
        print("form", form)
    lignes = Ligne.objects.all()

    return render(request, 'TravelTicket/admin/pages/ligne.html', {'form': form,'id_edit': id, 'lignes': lignes})



def ligne_delete(request, id):
    ligne = get_object_or_404(Ligne, id=id)
    ligne.delete()
    return redirect('ligne')



def assigneconducteur(request, id):
    car = get_object_or_404(Car, id=id)
    # assignform = AssignConducteurForm(request.POST or None, instance=conducteur)

    if request.method == 'POST':
        form = AssignConducteurForm(request.POST)
        if form.is_valid():
            conducteursSelect = form.cleaned_data['conducteur']


            for conducteur in conducteursSelect:
                conducteurup = Conducteur.objects.get(id=conducteur.id)
                conducteurup.car = car
                conducteurup.save(update_fields=['car'])
               
            return redirect('car')
    else:
        form = AssignConducteurForm()

    # conducteur = Conducteur.objects.filter(car__isnull=True)

    return redirect('car')

def desassigneconducteur(request, id):
    conducteurup = get_object_or_404(Conducteur, id=id)

    conducteurup.car=None
    conducteurup.save(update_fields=['car'])
          
    return redirect('car')
   

def segment(request):
    segments=Segment.objects.all()
    print("segments", segments)
    form = SegmentForm(request.POST or None)
    print("Segmentform", form)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        form.save()
        return redirect('segment')
    else:
            # Affiche toutes les erreurs dans la console
        print("Erreurs du formulaire:")
        for field, errors in form.errors.items():
            print(f"Champ {field}: {', '.join(errors)}")
            print("Données POST:", request.POST)
    return render(request, 'TravelTicket/admin/pages/segment.html', {'form': form,'segments': segments})


def segment_edit(request, id):
    segment_edit = Segment.objects.get(pk=id)
    # print("car",conducteur_edit.car)

    print("bien jouer ICI", segment_edit)
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = SegmentForm(request.POST, instance=segment_edit)
        print("bien jouerddf ICI")

        if form.is_valid():
            print("bien jouer")
            form.save()
            messages.success(request, "Segment enregistré avec succès !")

            return redirect('segment') 
    else:
        form = SegmentForm(instance=segment_edit)  
        print("form", form)
    segments = Segment.objects.all()

    return render(request, 'TravelTicket/admin/pages/segment.html', {'form': form,'id_edit': id, 'segments': segments})



def segment_delete(request, id):
    segment = get_object_or_404(Segment, id=id)
    segment.delete()
    return redirect('segment')





def tarif_management(request):
    segmentTypeCars = SegmentTypeCar.objects.all()
    print("tarif_management",SegmentTarifForm())
    if request.method == 'POST':
        segment = request.POST.get('segment')
        
        # Traitement de chaque tarif
        for key, value in request.POST.items():
            if key.startswith('tarif_'):
                typecar_id = key.split('_')[1]
                SegmentTypeCar.objects.update_or_create(
                    segment_id=segment,
                    typecar_id=typecar_id,
                    defaults={'tarif': int(value)}
                )
        return redirect('tarif_management')
    
    return render(request, 'TravelTicket/admin/pages/tarifsegment.html', {
        'form': SegmentTarifForm(),
        'segmentTypeCars': segmentTypeCars,
        'formtarif': SegmentTarifEditForm(),
        # 'id_edittarif':"0"
    })

# def load_tarif_fields(request):
#     print("load_tarif_fields")
#     segment_id = request.GET.get('segment') 
#     print("segment_id", segment_id)
#     segment = get_object_or_404(Segment, id=segment_id)
#     print("segment", segment)

#     if not segment_id:
#         print("pas de segment")
#         return JsonResponse({'html': ''})
    
#     # typecars = TypeCar.objects.filter(
#     #     segmenttypecar__segment_id=segment_id
#     # ).distinct()
#     typecars=segment.typevoyage.all()
#     print("typevoyage", typecars)

#     try:
#         # segment = Segment.objects.get(pk=segment_id)
#         # types_car = segment.typevoyage.all()
        
#         html = ""
#         for type_car in typecars:
#             html += f"""
#             <div class="form-group mb-3">
#                 <label class="form-label">Tarif pour {type_car.libele}</label>
#                 <input type="number" 
#                        name="tarif_{type_car.id}" 
#                        class="form-control"
#                        step="0.01"
#                        required>
#             </div>
#             """
        
#         return JsonResponse({'html': html})
    
#     except Segment.DoesNotExist:
#         return HttpResponse("<div class='alert alert-danger'>Segment introuvable</div>")

from django.http import JsonResponse

def load_tarif_fields(request):
    segment_id = request.GET.get('segment')
    if not segment_id:
        return JsonResponse({'html': '<div class="alert alert-danger">Aucun segment sélectionné</div>'})
    
    try:
        segment = Segment.objects.get(pk=segment_id)
        typecars = segment.typevoyage.all()
        
        if not typecars.exists():
            return JsonResponse({'html': '<div class="alert alert-info">Aucun type de véhicule associé à ce segment</div>'})
        
        html = ""
        for type_car in typecars:
            # Utilisez getattr pour éviter les erreurs si libele n'existe pas
            label = getattr(type_car, 'libele', f"Type {type_car.id}")
            
            html += f"""
            <div class="form-group mb-3">
                <label class="form-label">Tarif pour {label}</label>
                <input type="number" 
                       name="tarif_{type_car.id}" 
                       class="form-control"
                       step="0.01"
                       min="500"
                       required>
            </div>
            """
        
        return JsonResponse({'html': html})
    
    except Segment.DoesNotExist:
        return JsonResponse({'html': '<div class="alert alert-danger">Segment introuvable</div>'})
    except Exception as e:
        return JsonResponse({'html': f'<div class="alert alert-danger">Erreur: {str(e)}</div>'})
    



def segmenttarif_edit(request, id):
    segmenttarif_edit = SegmentTypeCar.objects.get(pk=id)
    # print("car",conducteur_edit.car)
    print("segment tarif  PPOOOOOD")

    print("bien jouer ICI", segmenttarif_edit)
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = SegmentTarifEditForm(request.POST, instance=segmenttarif_edit)
        print("bien jouerddf ICI")
        print("formtarifff", form)

        if form.is_valid():
            print("bien jouer")
            form.save()
            messages.success(request, "Segment enregistré avec succès !")

            return redirect('tarif_management') 
    else:
        form = SegmentTarifEditForm(instance=segmenttarif_edit, initial={
        'segment': str(segmenttarif_edit.segment),  # affichera "Abidjan -> Bouaké"
        'typecar': str(segmenttarif_edit.typecar),  # affichera "Car VIP", etc.
        })
        print("form", form)
    segmentTypeCars = SegmentTypeCar.objects.all()

    return render(request, 'TravelTicket/admin/pages/tarifsegment.html', {'formtarif': form,'id_edittarif': id, 'segmentTypeCars': segmentTypeCars, 'segmenttarif' : segmenttarif_edit})




def segmenttarif_delete(request, id):
    segmenttarif = get_object_or_404(SegmentTypeCar, id=id)
    segmenttarif.delete()
    return redirect('tarif_management')




def planning(request):
    plannings=Programme.objects.all()
    print("plannings", plannings)
    form = PlanningForm(request.POST or None)
    print("PlanningForm", form)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        programme = form.save()          
        dates = form.cleaned_data['date']
        horaires = form.cleaned_data['horaire']
        types = form.cleaned_data['typevoyage']
        print("dates", dates)
        print("horaires", horaires)
        print("types", types)

        for datev in dates:
            print("boucle for")
            for horaire in horaires:
                print("boucle for horaire")
                for typecar in types:
                    print("boucle for typecar")
                    voyage= Voyage.objects.create(
                            programme=programme,
                            date=datev,
                            horaire=horaire,
                            typecar=typecar
                    )
                    year = now().year
                    voyage.numerovoyage = f"V{year}{voyage.pk:03d}"
                    voyage.save()
                    print("voyage_numerovoyage", voyage.numerovoyage)
        return redirect('planning')
    else:
            # Affiche toutes les erreurs dans la console
        print("Erreurs du formulaire:")
        for field, errors in form.errors.items():
            print(f"Champ {field}: {', '.join(errors)}")
            print("Données POST:", request.POST)
    return render(request, 'TravelTicket/admin/pages/planning.html', {'form': form,'plannings': plannings})


def planning_edit(request, id):
    planning_edit = Programme.objects.get(pk=id)
    # print("car",conducteur_edit.car)

    print("bien jouer ICI planning_edit", planning_edit)
    print("METHOD:", request.method)



    if request.method == 'POST':
        form = PlanningForm(request.POST, instance=planning_edit)
        print("bien jouerddf ICI")

        if form.is_valid():
            print("bien jouer")
            form.save()

            messages.success(request, "planning modifié avec succès !")

            return redirect('planning') 
    else:
        form = PlanningForm(instance=planning_edit)  
        print("form", form)
    plannings = Programme.objects.all()

    return render(request, 'TravelTicket/admin/pages/planning.html', {'form': form,'id_edit': id, 'plannings': plannings})

def planning_delete(request, id):
    planning_delete = get_object_or_404(Programme, id=id)
    planning_delete.delete()
    return redirect('planning')


def voyage_planning(request, id):
    planning = Programme.objects.get(pk=id)  # print("car",conducteur_edit.car)
    print("bien jouer PLANNING ICI", planning)
    voyages_planning = Voyage.objects.filter(programme=planning)
    print("voyages_planning", voyages_planning)

    print("METHOD:", request.method)

    return render(request, 'TravelTicket/admin/pages/voyages_planning.html', {'voyages_planning': voyages_planning, 'planning': planning})


def assignation_ressource(request, id):
    voyage = get_object_or_404(Voyage, id=id)
    planning = voyage.programme
    # planning_id = get_object_or_404(Programme, planning=planning)
    print("planning_id", planning.id)
    voyages_planning=Voyage.objects.all()
    assignbtn=12333
    print('voyage_ Assignation_ressource', voyage)

    # le typecar lié au voyage (ex: VIP)
    typecar = voyage.typecar
    ligne=voyage.programme.ligne
    date=voyage.date
    print("date", date)
    print("ligne", ligne)
    print("typecar", typecar)
    departv=ligne.depart
    arriveev=ligne.arrive

    
    if request.method == 'POST':
        form = AssignationForm(request.POST, typecar=typecar, ligne=ligne, date=date)
       

        if form.is_valid():
            arrets_intermediaires = list(form.cleaned_data['arrets'])
            print("arrets_intermediaires", arrets_intermediaires)
            arrets_complets = [departv] + arrets_intermediaires + [arriveev]
            print("arrets_complets", arrets_complets)

            voyage.car = form.cleaned_data['car']
            voyage.conducteur = form.cleaned_data['conducteur']
            voyage.arrets.set(form.cleaned_data['arrets'])
            voyage.save()
            print("voyage.save debut")
            if voyage:
                print("voyage save")


                for i in range(len(arrets_complets)):
                    print("debut assigne segemnt")
                    for j in range(i + 1, len(arrets_complets)):
                        depart = arrets_complets[i]
                        arrivee = arrets_complets[j]
                        segmenttypecar = SegmentTypeCar.objects.get(
                        segment__villedepart=depart.ville,
                        segment__villearrivee=arrivee.ville,
                        typecar=typecar
                        )
                        print("segmenttypecar Pour elif", segmenttypecar)
                        if departv==depart:
                            heuredepart = voyage.horaire.heuredepart
                            print("heure depart", heuredepart)

                        # elif SegmentVoyage.objects.filter(segment__arrivee=depart.ville).exists():

                        #     heuredepart = SegmentVoyage.objects.get(segment__arrivee=depart.ville).heurearrivee
                        #     print("heure depart", heuredepart)
                        elif SegmentVoyage.objects.filter(segment=segmenttypecar).exists():
                            print("je suis entrer dans le elif")
                            heuredepart = SegmentVoyage.objects.get(segment=segmenttypecar).heurearrivee
                            print("heure depart", heuredepart)
                            

                        try:
                            segment = Segment.objects.get(villedepart=depart.ville, villearrivee=arrivee.ville)
                            print("depart.ville", depart.ville)
                            print("arrivee.ville", arrivee.ville)
                            print("typecar", typecar)
                            print("segment Disponoble aaaaaaaaaaaaaaaaaaaaaaaaa", segment)
                            segmenttypecar_select = SegmentTypeCar.objects.get(segment=segment, typecar=typecar)
                            print("segmenttypecar", segmenttypecar)
                            

                            heuredepart_dt = datetime.combine(datetime.today(), heuredepart)
                            duree_td = timedelta(hours=segment.duree.hour, minutes=segment.duree.minute, seconds=segment.duree.second)

                            heurearrivee_dt = heuredepart_dt + duree_td
                            heurearrivee = heurearrivee_dt.time()
                            print("heuredepart", heuredepart)
                            print("heurearrivee", heurearrivee)
                        

                            SegmentVoyage.objects.create(voyage=voyage, segment=segmenttypecar_select, plase_disponible=voyage.car.capacite, heuredepart=heuredepart, heurearrivee=heurearrivee, tarif=segmenttypecar_select.tarif)
                            print("segment crée succes", segmenttypecar_select)
                        except Segment.DoesNotExist:
                            print(f"Segment non trouvé : {depart} → {arrivee}")




            messages.success(request, "Assignation faite avec succès.")
            return redirect('voyage_planning',id=voyage.programme.id)  # ou autre page
    else:
        form = AssignationForm(typecar=typecar, ligne=ligne, date=date)

    return render(request, 'TravelTicket/admin/pages/voyages_planning.html', {
        'form': form,
        'voyages_planning': voyages_planning,
        'assignation': assignbtn,
        'voyage':voyage,
        'planning':planning

    })      




def get_conducteurs_by_car(request):
    print("get_conducteurs_by_car")
    car_id = request.GET.get('car_id')
    print("car_id", car_id)
    conducteurs_data = []

    if car_id:
        try:
            car = Car.objects.get(pk=car_id)
            conducteurs_data = list(car.conducteur_set.values('id', 'nom'))
        except Car.DoesNotExist:
            pass

    return JsonResponse({'conducteurs': conducteurs_data})


def changer_statut_voyage(request, id):
    voyage = get_object_or_404(Voyage, id=id)
    nouveau_statut = request.POST.get('nouveau_statut')

    if nouveau_statut not in ['Prévu', 'Effectué', 'Annulé', 'En cours']:
        messages.error(request, "Statut invalide.")
        return redirect('voyage_planning', id=voyage.programme.id)

    # Vérifier si le voyage a des réservations
    segmentvoyage = SegmentVoyage.objects.filter(voyage=voyage).first()
    has_reservations = Reservation.objects.filter(segmentvoyage__voyage=voyage).exists()

    # has_reservations = segmentvoyage.reservation_set.exists()  

    if has_reservations and nouveau_statut == 'Annulé':
        messages.warning(request, "Ce voyage a déjà des réservations et ne peut pas être annulé.")
        return redirect('voyage_planning', id=voyage.programme.id)

    voyage.statut = nouveau_statut
    voyage.save()
    messages.success(request, f"Statut mis à jour vers {nouveau_statut}.")
    return redirect('voyage_planning', id=voyage.programme.id)



def rechercher_voyages(request):
    segments_allers = []
    segments_retours = []
    date_depart = None
    date_precedente = None
    date_suivante = None
    ville_depart = ''
    ville_arrivee = ''
    type_voyage = 'aller_simple'
    nombre_place = 1
    gares = Gare.objects.all()
    voyages_info = []



    if request.method == 'GET' and 'date' in request.GET:
        ville_depart = request.GET.get('villedepart')
        ville_arrivee = request.GET.get('villearrivee')
        date_str = request.GET.get('date')
        type_voyage = request.GET.get('voyage_type', 'aller_simple')
        nombre_place = int(request.GET.get('Nombre_place', 1))
        print("date_str OKOKOKOKOKOKOk", date_str)

        try:
            print("verification date")
            date_depart = datetime.strptime(date_str, '%B %d, %Y').date()
        except ValueError:
            print("pas de date")
            date_depart = date.today()

        date_precedente = date_depart - timedelta(days=1)
        date_suivante = date_depart + timedelta(days=1)

        segments_allers = SegmentVoyage.objects.filter(
            segment__segment__villedepart__nom=ville_depart,
            segment__segment__villearrivee__nom=ville_arrivee,
            voyage__date__date=date_depart,
            voyage__statut="Prévu",
            plase_disponible__gt=0
        ).select_related('voyage', 'segment__segment').distinct()

        for segmentv in segments_allers:
                voyage_planning= segmentv.voyage


                arret_depart = next(

                    (arret for arret in voyage_planning.arrets.all() if arret.ville == segmentv.segment.segment.villedepart),

                        None

                    )
                arret_arrivee = next(

                    (arret for arret in voyage_planning.arrets.all() if arret.ville == segmentv.segment.segment.villearrivee),

                        segmentv.voyage.programme.ligne.arrive

                    )

                voyages_info.append({

                    'voyages': segments_allers,

                    'arret_depart': arret_depart,

                    'arret_arrivee': arret_arrivee

                    })
            


        # Formulaire reconstruit avec les valeurs précédentes
        form = TrajetHoraireForm(initial={
            'adress_depart': ville_depart,
            'adress_arrivee': ville_arrivee,
            'voyage_type': type_voyage,
            'Nombre_place': nombre_place,
            'date_depart': date_depart
        })


    elif request.method == 'POST':
        form = TrajetHoraireForm(request.POST)
        if form.is_valid():

            type_voyage = form.cleaned_data['voyage_type']
            ville_depart = form.cleaned_data['adress_depart']
            ville_arrivee = form.cleaned_data['adress_arrivee']
            date_depart = form.cleaned_data['date_depart']
            date_retour = form.cleaned_data.get('date_retour')
            nombre_place = form.cleaned_data['Nombre_place']
            print("date_retour", date_retour)
            print("date_depart", date_depart)
            date_precedente = date_depart - timedelta(days=1)

            # Date suivante (le lendemain)
            date_suivante = date_depart + timedelta(days=1)


        # la session
            request.session['nombre_place'] = nombre_place

            segments_allers = SegmentVoyage.objects.filter(
                
            segment__segment__villedepart__nom=ville_depart,
            segment__segment__villearrivee__nom=ville_arrivee,
            voyage__date__date=date_depart,
            voyage__statut="Prévu",
            plase_disponible__gt=0
            ).select_related('voyage', 'segment__segment').distinct()

            print("segments_allers", segments_allers)

            
            for segmentv in segments_allers:
                voyage_planning= segmentv.voyage
                print("segment.villedepart", segmentv.segment.segment.villedepart)
                print("depart",segmentv.voyage.programme.ligne.depart)
                print("voyage_planning.arrets.all", voyage_planning.arrets.all())

                arret_depart = next(

                    (arret for arret in voyage_planning.arrets.all() if arret.ville == segmentv.segment.segment.villedepart),

                        segmentv.voyage.programme.ligne.depart

                    )
                arret_arrivee = next(

                    (arret for arret in voyage_planning.arrets.all() if arret.ville == segmentv.segment.segment.villearrivee),

                        segmentv.voyage.programme.ligne.arrive

                    )

                voyages_info.append({

                    'voyages': segments_allers,

                    'arret_depart': arret_depart,

                    'arret_arrivee': arret_arrivee

                    })
            

 

            #  Recherche retour (si aller-retour)
            if type_voyage == 'aller_retour' and date_retour:
                segments_retours = SegmentVoyage.objects.filter(
                    segment__villedepart__nom=ville_arrivee,
                    segment__villearrivee__nom=ville_depart,
                    voyage__date__date=date_retour,
                    voyage__statut="Prévu",
                    plase_disponible__gt=0
                ).select_related('voyage', 'segment').distinct()

    else:
        form = TrajetHoraireForm()
    print("voyages_info", voyages_info)

    return render(request, 'TravelTicket/voyage/searchresult.html', {
        'form': form,
        'segments_allers': segments_allers,
        'segments_retours': segments_retours,
        'date_precedente': date_precedente,
        'date_suivante': date_suivante,
        'date_depart' : date_depart,
        'ville_depart': ville_depart,
        'ville_arrivee': ville_arrivee,
        'type_voyage': type_voyage,
        'nombre_place': nombre_place,
        'gares': gares,
        'voyages_info': voyages_info

    })




def  reserver_voyage(request, id):
    seg_voyage_id = id
    print("seg_voyage_id", seg_voyage_id)
    print("id", id)
    nombre_places = request.session.get('nombre_place')
    voyage = get_object_or_404(SegmentVoyage, pk=id)
    voyage_complete = voyage.voyage
    ligne = voyage_complete.programme.ligne
    voyage_depart=ligne.depart.ville
    voyage_arrivee=ligne.arrive.ville
    arrets = [arret.ville for arret in voyage_complete.arrets.all()]
    ville_voyage= [voyage_depart] + arrets + [voyage_arrivee]  
    print("ville_voyage", ville_voyage) 
    index_depart = ville_voyage.index(voyage.segment.segment.villedepart)
    index_arrivee = ville_voyage.index(voyage.segment.segment.villearrivee)

    villes_concernees_reservation = ville_voyage[index_depart:index_arrivee]
    print("Villes concernées :", villes_concernees_reservation)
    segments_voyage=SegmentVoyage.objects.filter(voyage=voyage_complete)

    

    print("voyage_complete", voyage_complete)
    
    PassagerFormSet = modelformset_factory(Passager, form=PassagerForm, extra=nombre_places)

    if request.method == 'POST':
        formset = PassagerFormSet(request.POST)
        destination_form = DestinationForm(request.POST)
        print("destination_form", destination_form)
        print("formset", formset)

        if formset.is_valid() and destination_form.is_valid():
            destination = destination_form.cleaned_data['destination']
            for form in formset:
                if form.cleaned_data:
                    passager = form.save(commit=False)
                    passager.destination = destination
                    passager.save()
                    print("passager Passager", passager)
                    reservation=Reservation.objects.create(
                        # client=request.user,
                        segmentvoyage=voyage,
                        passager=passager,
                        montant_reservation=voyage.tarif
                    )
                    reservation.save()
                    print("passager_reservation", passager)
                    print("reservation", reservation)

                    if reservation:
                        
                        for segment_voyage in segments_voyage:
                            if segment_voyage.segment.segment.villedepart in villes_concernees_reservation or segment_voyage.segment.segment.villearrivee in villes_concernees_reservation:
                                segment_voyage.plase_disponible -= 1
                                segment_voyage.save()
                            




                    
            return redirect('payement')
    else:
        formset = PassagerFormSet(queryset=Passager.objects.none())
        destination_form = DestinationForm()

    return render(request, 'TravelTicket/voyage/reservation.html', {
        'formset': formset,
        'destination_form': destination_form,
        'seg_voyage_id': seg_voyage_id

    })


def payement(request):
    return render(request, 'TravelTicket/voyage/payement.html')
