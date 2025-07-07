


from datetime import date, timedelta
from django import forms

from TravelTicket.models import Avantage, Car, Client, Conducteur, Date, Gare, Horaire, Ligne, Passager, Programme, Segment, SegmentTypeCar, TypeCar, Ville, Voyage

"""
class TrajetForm(forms.ModelForm):
    class Meta:
        model = Trajet
        model = Horaire
        fields = ['adress_depart', 'adress_arrivee', 'date_depart']
        widgets ={
            'date_depart': forms.DateInput(attrs={
                'type': 'date',
                'min': date.today().isoformat(),
                'value': date.today().isoformat()

            }
            ),
        }
"""

def get_ville_choices():
        villes = Ville.objects.all().order_by('nom')
        return [(ville.nom, ville.nom) for ville in villes]

def get_default_ville():
    ville = Ville.objects.all().order_by('nom').last()
    return ville.nom if ville else None
    
# class TrajetHoraireForm(forms.Form):


#     adress_depart = forms.ChoiceField(choices=get_ville_choices , widget=forms.Select(attrs={'class': 'form-select'}))
#     adress_arrivee = forms.ChoiceField(choices=get_ville_choices, initial=get_default_ville  , widget=forms.Select(attrs={'class': 'form-select'}))
#     date_depart = forms.DateField(widget=forms.DateInput(attrs={
#         'type': 'date',
#         'min': date.today().isoformat(),
#         'value': date.today().isoformat()
#     }))

#     Nombre_place=forms.IntegerField(initial=1, min_value=1 , widget=forms.NumberInput(attrs={'class': 'form-control'}))




class TrajetHoraireForm(forms.Form):
    VOYAGE_CHOICES = [
            ('aller_simple', 'Aller simple'),
            ('aller_retour', 'Aller retour'),
        ]
        
    voyage_type = forms.ChoiceField(
            choices=VOYAGE_CHOICES,
            widget=forms.RadioSelect(attrs={
                'class': 'btn-check voyage-type-btn',
            }),
            initial='aller_simple',
            label=""
        )
    
    # Champ adresse départ
    adress_depart = forms.ChoiceField(
        choices=get_ville_choices,
        widget=forms.Select(attrs={
            'class': 'form-control ps-1 py-1 border-start-0',
            'placeholder': 'Ville ou gare'
        }),
        label="De"
    )
    
    # Champ adresse arrivée
    adress_arrivee = forms.ChoiceField(
        choices=get_ville_choices,
        initial=get_default_ville,
        widget=forms.Select(attrs={
            'class': 'form-control ps-1 py-1 border-start-0',
            'placeholder': 'Ville ou gare'
        }),
        label="À"
    )
    
    # Champ date départ
    date_depart = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control ps-1 py-1 border-start-0 datepicker',
            'type': 'date',
            # 'placeholder': 'jj/mm/aaaa',
            'min': date.today().isoformat(),
            'value': date.today().isoformat()
        }),
        label="Date départ"
    )
    
    # Champ date retour (optionnel)
    date_retour = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control ps-1 py-1 border-start-0 datepicker',
            'type': 'date',
            # 'placeholder': 'jj/mm/aaaa'
            'min': date.today().isoformat(),
            'value': date.today().isoformat()
        }),
        label="Date retour"
    )
    
    # Champ nombre de places
    Nombre_place = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ps-1 py-1 border-start-0',
        }),
        label="Nombre place"
    )

    def clean(self):
        cleaned_data = super().clean()
        voyage_type = cleaned_data.get('voyage_type')
        date_retour = cleaned_data.get('date_retour')
        date_depart = cleaned_data.get('date_depart')

        if voyage_type == 'aller_retour' and not date_retour:
            self.add_error('date_retour', "Ce champ est obligatoire pour un aller-retour")
        
        if voyage_type == 'aller_retour' and date_retour and date_depart:
            if date_retour < date_depart:
                self.add_error('date_retour', "La date de retour doit être après la date de départ")
        
        return cleaned_data
    

class CityForm(forms.Form):
    nom = forms.CharField(
        label="",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez le nom de la ville'
        })
    )
    
    region = forms.CharField(
        label="",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Entrez la région'
        })
    )



class TypeCarForm(forms.ModelForm):
    class Meta:
        model = TypeCar
        fields = ['libele', 'description', 'avantages']
        widgets = {
            'libele': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'id': 'titre',
                'placeholder': 'Ex: Car Luxe, Car Économique',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'description',
                'rows': 3,
                'placeholder': 'Décrivez les caractéristiques principales'
            }),
            'avantages': forms.SelectMultiple(attrs={
                'class': 'form-select ',
                'id': 'avantagesSelect',
                'multiple': 'multiple'

            }),
        }
        labels = {
            'libele': 'Titre du type*',
            'description': 'Description',
            'avantages': 'Avantages'
        }

class AvantageCarForm(forms.ModelForm):
    class Meta:
        model = Avantage
        fields = ['libele', 'description']
        widgets = {
            'libele': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'avantage',
                'placeholder': 'Ex: Car Luxe, Car Économique',
                'required': 'required'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'description',
                'rows': 3,
                'placeholder': 'Décrivez les caractéristiques principales',
                'required': 'required'
            }),
            
        }
        labels = {
            'description': 'Description',
            'libele': 'Avantage'
        }


class ConducteurForm(forms.ModelForm):
    class Meta:
        model = Conducteur
        fields = ['nom', 'prenom', 'contact','car']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'id': 'nom',
                'placeholder': ' le nom',
                'required': 'required'
            }),

            'prenom': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'id': 'prenom',
                'placeholder': ' le prenom',
                'required': 'required'
            }),

            'contact': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'id': 'contact',
                'placeholder': ' Ex : 06 00 00 00 00',
                'required': 'required',
                'maxlength': '14'
                
            }),
            'car': forms.Select(attrs={
                'id': 'car',
                'class': 'form-control',
                'required': False  
            })
            
        }
        labels = {
            'nom': 'Nom*',
            'prenom': 'Prenom',
            'contact': 'Contact',
            'car': 'Car'

        }




class CarForm(forms.ModelForm): 
    class Meta:
        model = Car
        fields = ['immatriculation', 'model', 'couleur', 'typecar', 'capacite']
        widgets = {
            'immatriculation': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'immatriculation',
                'placeholder': 'Ex: CIAA33444FFA',
                'required': 'required'
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'model',
                'placeholder': 'Ex: BMW',
                'required': 'required'
            }),
            'couleur': forms.Select(attrs={
                'id': 'couleur',
                'class': 'form-control',
                'required': 'required'
            }),
            'typecar': forms.Select(attrs={
                'class': 'form-control',
                'id': 'typecar',
                'required': 'required'
            }),
            'capacite': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'capacite',
                'required': 'required'
            }),
            # 'conducteur': forms.Select(attrs={
            #     'id': 'conducteur',
            #     'class': 'form-control',
            # })
        }

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        # # Montrer uniquement les conducteurs qui ne sont associés à aucun car
        #     self.fields['conducteur'].queryset = Conducteur.objects.filter(car__isnull=True)


class GareForm(forms.ModelForm): 
    class Meta:
        model = Gare
        fields = ['nom', 'ville', 'adresse', 'contact', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'nom',
                'placeholder': 'Nom ',
                'required': 'required'
            }),
            'ville': forms.Select(attrs={
                'class': 'form-control',
                'id': 'ville',
                'placeholder': 'Ville Implantation ',
                'required': 'required'
            }),
            'adresse': forms.TextInput(attrs={
                'id': 'adresse',
                'class': 'form-control',
                'placeholder': 'adresse/ Commune/Quartier/ Lieu reconnus',

                'required': 'required'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'contact',
                'required': 'required',
                'maxlength': '14'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'email',
                'required': 'required'
            }),
          
        }
        def clean_contact(self):
            contact = self.cleaned_data['contact']
            if Conducteur.objects.filter(contact=contact).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ce numéro de contact est déjà utilisé.")
            return contact


class LigneForm(forms.ModelForm):
    class Meta:
        model = Ligne
        fields = ['depart', 'arrive','villeligne']
        widgets = {
            'depart': forms.Select(attrs={
                'class': 'form-control form-control',
                'id': 'depart',
                'placeholder': 'Ex: Car Luxe, Car Économique',
                'required': 'required'
            }),
            'arrive': forms.Select(attrs={
                'class': 'form-control form-control',
                'id': 'arrive',
                'placeholder': 'Ex: Car Luxe, Car Économique',
                'required': 'required'
            }),
            'villeligne': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'id': 'villeligne',
                'required': 'required',
                'multiple': 'multiple',
                'style': 'width: 100%;'
            }),
            # 'duree': forms.NumberInput(attrs={
            #     'class': 'form-control',
            #     'id': 'duree',
            #     'required': 'required'
            # }),
            
            
        }
        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     self.fields['depart'].empty_label = "Sélectionnez Départ"


        

# class AssignConducteurForm(forms.Form):
#     # Champ pour sélectionner un conducteur sans car
#     conducteur = forms.ModelMultipleChoiceField(
#         queryset=Conducteur.objects.filter(car__isnull=True),
#         widget=forms.SelectMultiple(attrs={
#             'class': 'form-select select2-multiple',
#             'data-placeholder': 'Sélectionnez des conducteurs',
#             'multiple': 'multiple',
#             'id': 'conducteurassigne'
#         })
#     )

class AssignConducteurForm(forms.Form):
    conducteur = forms.ModelMultipleChoiceField(
        queryset=Conducteur.objects.filter(car__isnull=True),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select select2-multiple',
            'data-placeholder': 'Sélectionnez des conducteurs',
            'style': 'width: 100%',
            'multiple': 'multiple',
            'id': 'conducteurassigne'
        })
    )


class SegmentForm(forms.ModelForm):
    class Meta:
        model = Segment
        fields = ['villedepart','villearrivee','typevoyage','duree']
        widgets = {
            'villedepart': forms.Select(attrs={
                'class': 'form-control form-control',
                'id': 'villedepart',
                'placeholder': 'Ex: Abidjan',
                'required': 'required'
            }),
            'villearrivee': forms.Select(attrs={
                'class': 'form-control form-control',
                'id': 'villearrivee',
                'placeholder': 'Ex: Korhogo',
                'required': 'required'
            }),
            'typevoyage': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'id': 'typevoyage',
                'required': 'required',
                'multiple': 'multiple',
                # 'style': 'width: 100%;'
            }),
            'duree': forms.TimeInput(attrs={
                'class': 'form-control',
                'id': 'duree',
                'required': 'required',
                'placeholder': 'HH:MM:SS',
                'type': 'time',
                'step': '1'
            }),
            
            
        }

    # def clean_duree(self):
    #     time_obj = self.cleaned_data.get('duree')
    #     if not time_obj:
    #         return None
            
    #     # Convertit l'objet time en timedelta
    #     return timedelta(
    #         hours=time_obj.hour,
    #         minutes=time_obj.minute,
    #         seconds=time_obj.second
    #     )




    # forms.py

class SegmentTarifForm(forms.Form):
    segment = forms.ModelChoiceField(
        queryset=Segment.objects.all(),
        # label="Choisissez un segment",
        widget=forms.Select(attrs={
            'id': 'segment-select',
            'hx-get': '/load-typecar-fields/',
            'hx-target': '#typecar-fields',
            'hx-trigger': 'change',
            'class': 'form-select form-control'
        })
    )
  

class SegmentTarifEditForm(forms.ModelForm):
    class Meta:
        model = SegmentTypeCar
        fields = ['segment','typecar','tarif']
        widgets = {
            'segment': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'id': 'segment',
                # 'placeholder': 'Ex: Abidjan',
                'disabled': 'disabled',
                'required': 'required'
            
            }),
            'typecar': forms.TextInput(attrs={
                'class': 'form-control form-control',
                'id': 'typecar',
                # 'placeholder': 'Ex: Korhogo',
                'disabled': 'disabled',
                'required': 'required'
            }),
            'tarif': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'tarif',
                'required': 'required',
                # 'style': 'width: 100%;'
            }),
       
            
            
        }



class PlanningForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ['ligne','typevoyage','date','horaire']
        widgets = {
            'ligne': forms.Select(attrs={
                'class': 'form-control form-control',
                'id': 'ligne',
                'placeholder': 'Ex: Abidjan',
                'required': 'required'
            }),
            'typevoyage': forms.SelectMultiple(attrs={
                'class': 'form-control form-control',
                'id': 'typevoyage',
                'multiple': 'multiple',
                'required': 'required'
            }),
            'date': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'id': 'date',
                'required': 'required',
                'multiple': 'multiple',
              
                # 'style': 'width: 100%;'
            }),
              'horaire': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'id': 'horaire',
                'required': 'required',
                'multiple': 'multiple',
                # 'style': 'width: 100%;'
            }),
         
        }
    

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            date_debut = date.today()
            date_fin = date.today() + timedelta(days=14)

            # Filtrer les dates valides
            self.fields['date'].queryset = Date.objects.filter(date__range=(date_debut, date_fin))


class AssignationForm(forms.Form):
    car = forms.ModelChoiceField(
        queryset=Car.objects.none(),  # par défaut vide
        label="Car",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    conducteur = forms.ModelChoiceField(
        queryset=Conducteur.objects.all(),
        label="Conducteur",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    arrets = forms.ModelMultipleChoiceField(
        queryset=Gare.objects.all(),
        label="Arrêts",
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple'})
    )

    def __init__(self, *args, **kwargs):
        typecar = kwargs.pop('typecar', None)
        ligne = kwargs.pop('ligne', None)
        date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)

        if ligne is not None:
            self.fields['arrets'].queryset = ligne.villeligne.all()
        else:
            print("ligne est None")
            self.fields['arrets'].queryset = Gare.objects.none()
            print("Ligne_Gare_servies", ligne.villeligne.all())
            self.fields['arrets'].queryset = ligne.villeligne.all()

        if typecar and ligne and date:
            # Récupérer les cars du bon type
            cars_dispo = Car.objects.filter(typecar=typecar)
            print("cars_dispo", cars_dispo)

            # Exclure les cars déjà affectés à un voyage sur cette ligne à cette date
            cars_utilises = Voyage.objects.filter(
                date=date,
                programme__ligne=ligne,
                car__isnull=False
            ).values_list('car_id', flat=True)
            print("cars_utilises", cars_utilises)
            print("date", date)
            # self.fields['car'].queryset = cars_dispo
            # if cars_utilises.exists():
            self.fields['car'].queryset = cars_dispo.exclude(id__in=cars_utilises)
            # else:
            #     self.fields['car'].queryset = cars_dispo

        
        else:
            self.fields['car'].queryset = Car.objects.none()


class PassagerForm(forms.ModelForm):
    class Meta:
        model = Passager
        fields = ['nom', 'prenoms','mugepci','destination']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'placeholder': 'Entrez le nom'
            }),
            'prenoms': forms.TextInput(attrs={
                'class': 'form-control py-2',
                'placeholder': 'Entrez les prénoms'
            }),

            'mugepci': forms.TextInput(attrs={
                'class': 'form-control py-2',
            }),
            'destination': forms.Select(attrs={
                'class': 'form-control py-2',
            }),
        }

class DestinationForm(forms.Form):
    destination = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control py-2',
            'placeholder': 'Ex: Napie'   
        }),
    )





# class ClientForm(forms.ModelForm):
#     class Meta:
#         model = Client
#         fields = ['nom', 'prenoms', 'email', 'telephone']
#         widgets = {
#             'nom': forms.TextInput(attrs={'class': 'form-control'}),
#             'prenoms': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'telephone': forms.TextInput(attrs={'class': 'form-control'}),
#         }

    
