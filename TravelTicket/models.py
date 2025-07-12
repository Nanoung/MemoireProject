import datetime
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class Ville(models.Model):
        nom=models.CharField(max_length=100)
        region=models.CharField(max_length=100)
        longitude=models.FloatField( null=True, blank=True)
        latitude=models.FloatField( null=True, blank=True)
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)
        def __str__(self):
            return f"{self.nom}"
        
class Gare(models.Model):
        nom=models.CharField(max_length=100)
        ville=models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='ville')
        adresse=models.CharField(max_length=100)
        longitude=models.FloatField( null=True, blank=True)
        latitude=models.FloatField( null=True, blank=True)
        contact=models.CharField(max_length=14,null=True, blank=True)
        email=models.EmailField(null=True,max_length=100)
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)
        
        def __str__(self):
            return f"{self.ville}({self.nom})"
        
class Image(models.Model):
        gare=models.ForeignKey(Gare, on_delete=models.CASCADE ,related_name='images')
        image=models.ImageField(upload_to='images/')
        def __str__(self):
            return f"{self.image}"
        
class Profil(models.Model):
        codeprofil=models.CharField(max_length=100)
        libele=models.CharField(max_length=100)

        def __str__(self):
            return f"{self.nom}"
        
class User(models.Model):
        email=models.EmailField(unique=True)
        password=models.CharField(max_length=100)
        telephone=models.CharField(max_length=100)
        nom=models.CharField(max_length=100)
        prenom=models.CharField(max_length=100)
        profil=models.ForeignKey(Profil, on_delete=models. PROTECT)
        gare=models.ForeignKey(Gare, on_delete=models. CASCADE) #relation manytomany
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"{self.email}" 
        
class Avantage(models.Model):
    libele = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f" {self.libele}"
        

class TypeCar(models.Model): #car
        libele=models.CharField(max_length=100)
        description=models.TextField()
        avantages=models.ManyToManyField(Avantage)
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)
        def __str__(self):
            return f"{self.libele}"
        


        

class Car(models.Model):
        COULEUR_CHOICES = (
            ('Blanc', 'Blanc'),
            ('Noir', 'Noir'),
            ('Rouge', 'Rouge'),
            ('Vert', 'Vert'),
            ('Bleu', 'Bleu'),
            ('Gris', 'Gris'),
            ('Jaune', 'Jaune'),
            ('Orange', 'Orange'),
            ('Marron', 'Marron'),
            ('Violet', 'Violet'),
        )
        immatriculation=models.CharField(max_length=100)
        model=models.CharField(max_length=100)
        typecar=models.ForeignKey(TypeCar, on_delete=models.PROTECT)
        couleur = models.CharField(max_length=100, choices=COULEUR_CHOICES)
        capacite=models.IntegerField()
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)
        def __str__(self):
            return f"{self.immatriculation}"
        



class Conducteur(models.Model):
        # tarccar=models.CharField(max_length=100)
        nom=models.CharField(max_length=100)
        prenom=models.CharField(max_length=100)
        contact=models.CharField(max_length=14, unique=True)
        car=models.ForeignKey(Car, on_delete=models.SET_NULL ,blank=True, null=True)        
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)
        def __str__(self):
            return f"{self.nom} {self.prenom}"
        

class Date(models.Model):
    date= models.DateField()
    def __str__(self):
        return f"{self.date}"

class Ligne(models.Model):
    depart=models.ForeignKey(Gare, on_delete=models.CASCADE , related_name='depart')
    arrive=models.ForeignKey(Gare, on_delete=models.CASCADE,  related_name='arrive')
    villeligne=models.ManyToManyField(Gare , related_name='villeligne') # ici Villeligne representeles gare servis par la ligne, pour ne pas faire trop de changement dans le code, je laisse intacte cette relation
    # duree=models.FloatField()
    datecreate=models.DateTimeField(auto_now_add=True)
    dateupdate=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.depart} -> {self.arrive}"
    
class Horaire(models.Model):
        heuredepart=models.TimeField()
        def __str__(self):
            return f"{self.heuredepart}"


class Programme(models.Model):
        ligne=models.ForeignKey(Ligne, on_delete=models.CASCADE)
        typevoyage=models.ManyToManyField(TypeCar)
        date=models.ManyToManyField(Date)
        horaire=models.ManyToManyField(Horaire)
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)
        def __str__(self):
            return f"{self.ligne}"

class Voyage(models.Model):
    numerovoyage = models.CharField(max_length=100, editable=False, unique=True,default=uuid.uuid4)
    programme = models.ForeignKey('Programme', on_delete=models.CASCADE)
    date = models.ForeignKey(Date, on_delete=models.CASCADE)
    horaire = models.ForeignKey(Horaire, on_delete=models.CASCADE)
    typecar = models.ForeignKey(TypeCar, on_delete=models.CASCADE)
    car = models.ForeignKey('Car', on_delete=models.SET_NULL, null=True, blank=True)
    conducteur = models.ForeignKey('Conducteur', on_delete=models.SET_NULL, null=True, blank=True)
    arrets=models.ManyToManyField(Gare, blank=True)
    datecreates=models.DateTimeField(auto_now_add=True)
    dateupdates=models.DateTimeField(auto_now=True)
    statut = models.CharField(max_length=50, choices=[('Prévu', 'Prévu'), ('Effectué', 'Effectué'), ('Annulé', 'Annulé'), ('En cours', 'En cours')], default='Prévu')

    def __str__(self):
        return f"{self.programme.ligne} | {self.date} - {self.horaire} ({self.typecar})"

class Position(models.Model): # les position sont enregistrées si le voyage est en cours
    longitude = models.FloatField()
    latitude = models.FloatField()
    voyage = models.ForeignKey(Voyage, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    adresse = models.CharField(max_length=255) # via geocoding a faire apres

    def __str__(self):
        return f"{self.voyage} | {self.adresse} | {self.longitude}, {self.latitude}"

class Segment(models.Model):
        villedepart=models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='villedepart')
        villearrivee=models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='villearrivee')
        typevoyage=models.ManyToManyField(TypeCar)
        duree=models.TimeField()
        distance=models.DurationField( null=True, blank=True)
        def __str__(self):
            return f"{self.villedepart} <----------> {self.villearrivee}"
        

# cette classe gere les tarif de segment par type de voiture    
class SegmentTypeCar(models.Model):
        segment=models.ForeignKey(Segment, on_delete=models.CASCADE , related_name='segment')
        typecar=models.ForeignKey(TypeCar, on_delete=models.CASCADE , related_name='typecar')
        tarif=models.IntegerField()
        def __str__(self):
            return f"{self.segment} -> {self.typecar} -> {self.tarif}"
        class Meta:
            unique_together = ('segment', 'typecar')


class SegmentVoyage(models.Model):
    segment=models.ForeignKey(SegmentTypeCar, on_delete=models.CASCADE)
    voyage=models.ForeignKey(Voyage, on_delete=models.CASCADE)
    plase_disponible = models.IntegerField(default=0) # nombre de place disponible par defaut Capacité du car
    heuredepart=models.TimeField()
    heurearrivee=models.TimeField(null=True , blank=True)
    tarif=models.IntegerField(default=0)
    datecreate=models.DateTimeField(auto_now_add=True)
    dateupdate=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.segment} -> {self.voyage}"
    



# Gestionnaire du modèle Client

class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15, unique=True)
    mugepci = models.CharField(max_length=100, null=True , blank=True, unique=True)
    datecreate=models.DateTimeField(auto_now_add=True)
    dateupdate=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nom} {self.prenoms}"


class Passager(models.Model):
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    mugepci = models.CharField(max_length=100, null=True , blank=True, unique=True)
    destination=models.CharField(max_length=100, null=True , blank=True)
    datecreate=models.DateTimeField(auto_now_add=True)
    dateupdate=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nom} {self.prenoms}"
    

class Payement(models.Model): # Si payement modifier la reservation pour mettre en validé.
    client= models.ForeignKey(Client, on_delete=models.PROTECT,null=True, blank=True)
    montant=models.DecimalField(max_digits=10, decimal_places=2)
    modepayement=models.CharField(max_length=100)
    reference=models.CharField(max_length=100)
    numeropayement=models.CharField(max_length=100) # en Gare(Espèces), En lige (Mobile money)
    datepayement=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.reservation} -> {self.montant}"
    
    
class Reservation(models.Model):
      
    segmentvoyage= models.ForeignKey(SegmentVoyage,  on_delete=models.CASCADE, null=True)
    client= models.ForeignKey(Client,on_delete=models.SET_NULL, null=True, blank=True)
    passager= models.ForeignKey(Passager,on_delete=models.SET_NULL, null=True, blank=True,related_name='passager')
    numero_reservation = models.CharField(max_length=100, editable=False, unique=True , null=True , blank=True)  # Numéro de réservation unique
    places_reservees = models.PositiveIntegerField(default=1)  # Nombre de places réservées
    montant_reservation=models.DecimalField(max_digits=10, decimal_places=2 , default=0)
    montant_a_payer=models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=[('Annulé', 'Annulé'), ('Validé', 'Validé'), ('En attente', 'En attente')],default='En attente')
    numeropayement=models.ForeignKey(Payement, on_delete=models.PROTECT, null=True , blank=True)
    panier_code = models.CharField(max_length=100, null=True, blank=True)
    datereservation = models.DateTimeField(auto_now_add=True) 
    dateupdate=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.numero_reservation:
            self.numero_reservation = f"RES-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} -> {self.segmentvoyage}-> {self.passager}"
    
class Remise(models.Model):
    libele=models.CharField(max_length=100)
    montant=models.IntegerField()
    datecreate=models.DateTimeField(auto_now_add=True)
    dateupdate=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.libele} -> {self.montant}"
    


 

# from django.db.models.signals import post_migrate
# from django.dispatch import receiver

# @receiver(post_migrate)
# def create_dates_for_year(sender, **kwargs):
#     from .models import Date  # pour éviter les problèmes d'importation circulaire
#     if sender.name != "TravelTicket":
#         return  # Évite que ça tourne pour les autres apps

#     year = datetime.date.today().year
#     start = datetime.date(year, 1, 1)
#     end = datetime.date(year, 12, 31)

#     current = start
#     created_count = 0
#     while current <= end:
#         obj, created = Date.objects.get_or_create(date=current)
#         if created:
#             created_count += 1
#         current += datetime.timedelta(days=1)

#     print(f"✔ {created_count} dates créées pour l'année {year}")