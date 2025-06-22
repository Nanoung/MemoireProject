import base64
from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
import requests

from TravelTicket.models import Car, Conducteur, Gare, Image, Ligne, Segment, SegmentTypeCar, TypeCar, Ville
from TravelTicket.forms import AssignConducteurForm, AvantageCarForm, CarForm, CityForm, ConducteurForm, GareForm, LigneForm, SegmentForm, SegmentTarifEditForm, SegmentTarifForm, TrajetHoraireForm, TypeCarForm
from geopy.geocoders import Nominatim
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


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
    TRACCAR_SERVER ="https://8d44-196-47-128-150.ngrok-free.app"
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
    TRACCAR_SERVER ="https://8d44-196-47-128-150.ngrok-free.app"
    API_USER = "admin"
    API_PASSWORD = "admin"
    conducteur = get_object_or_404(Conducteur, id=id)
    search_response_position = requests.get(
        f"{TRACCAR_SERVER}/api/devices?uniqueId=Nanou20",
        headers={'Authorization': 'Basic ' + base64.b64encode(f"{API_USER}:{API_PASSWORD}".encode()).decode()}
        )
    print( "search_response_position",search_response_position.json())

    # 1. Récupérer le positionId depuis la réponse de l'appareil
    position_id = search_response_position.json()[0].get("positionId")
    print( "position_id",position_id)

    # 2. Requête pour obtenir les détails de la position

    position_response = requests.get(
        f"{TRACCAR_SERVER}/api/positions?id={position_id}",
        headers={
            "Authorization": "Basic " + base64.b64encode(f"{API_USER}:{API_PASSWORD}".encode()).decode()
        }
    )
    print( "position_response",position_response.json())
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


