import base64
from pyexpat.errors import messages
from django.shortcuts import get_object_or_404, redirect, render
import requests

from TravelTicket.models import Car, Conducteur, Gare, Image, TypeCar, Ville
from TravelTicket.forms import AvantageCarForm, CarForm, CityForm, ConducteurForm, GareForm, TrajetHoraireForm, TypeCarForm
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
                messages.success(request, "Conducteur et appareil créés avec succès!")
            else:
                raise Exception(f"Erreur création appareil: {device_response.text}")
            
            conducteur.save()
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
    conducteur = get_object_or_404(Conducteur, id=id)
    conducteur.delete()
    return redirect('conducteur')



def car(request):
    cars=Car.objects.all()
    form = CarForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        form.save()
        return redirect('car')  # Remplace par ta route cible
    return render(request, 'TravelTicket/admin/pages/Cars.html', {'form': form,'cars': cars})


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