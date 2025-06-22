import datetime
import uuid
from django.db import models

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
        contact=models.CharField(max_length=14)
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
    date= models.DateTimeField()  # Date et heure de départ

class Ligne(models.Model):
    depart=models.ForeignKey(Gare, on_delete=models.CASCADE , related_name='depart')
    arrive=models.ForeignKey(Gare, on_delete=models.CASCADE,  related_name='arrive')
    villeligne=models.ManyToManyField(Ville , related_name='villeligne')
    # duree=models.FloatField()
    datecreate=models.DateTimeField(auto_now_add=True)
    dateupdate=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.depart} -> {self.arrive}"
    
class Horaire(models.Model):
        heuredepart=models.TimeField()
        def __str__(self):
            return f"{self.heuredepart} -> {self.heurearrivee}"


class Programme(models.Model):
        ligne=models.ForeignKey(Ligne, on_delete=models.CASCADE)
        typevoyage=models.ManyToManyField(TypeCar)
        date=models.ManyToManyField(Date)
        Horaire=models.ManyToManyField(Horaire)
        datecreate=models.DateTimeField(auto_now_add=True)
        dateupdate=models.DateTimeField(auto_now=True)
        def __str__(self):
            return f"{self.villedepart} <-> {self.villearrivee}"

class Segment(models.Model):
        villedepart=models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='villedepart')
        villearrivee=models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='villearrivee')
        typevoyage=models.ManyToManyField(TypeCar)
        duree=models.TimeField()
        distance=models.DurationField( null=True, blank=True)
        def __str__(self):
            return f"{self.villedepart} -> {self.villearrivee}"
        
        # class Meta:
        #     unique_together = ('villedepart', 'villearrivee')

# cette classe gere les tarif de segment par type de voiture    
class SegmentTypeCar(models.Model):
        segment=models.ForeignKey(Segment, on_delete=models.CASCADE)
        typecar=models.ForeignKey(TypeCar, on_delete=models.CASCADE)
        tarif=models.IntegerField()
        def __str__(self):
            return f"{self.segment} -> {self.typecar} -> {self.tarif}"
        class Meta:
            unique_together = ('segment', 'typecar')

class SegmentHoraire(models.Model):
    heuredepart = models.TimeField()   
    heurearrivee = models.TimeField(null=True , blank=True)
    def __str__(self):
         return f"{self.heuredepart}"

class SegmentSegmentHoraire(models.Model):
    segment= models.ForeignKey(Segment, on_delete=models.CASCADE )
    segmenthoraire = models.ForeignKey(SegmentHoraire, on_delete=models.CASCADE)
    placedisponible = models.IntegerField(default=0)

    class Meta:
        unique_together = ('segment', 'segmenthoraire')


class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenoms = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    datecreate=models.DateTimeField(auto_now_add=True)
    dateupdate=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.nom} {self.prenoms}"
    
class Reservation(models.Model):
      
    voyage= models.ForeignKey(SegmentSegmentHoraire,  on_delete=models.CASCADE, related_name='reservations' , null=True)
    client= models.ForeignKey(Client, on_delete=models.PROTECT)
    numero_reservation = models.CharField(max_length=100, editable=False, unique=True , null=True , blank=True)  # Numéro de réservation unique
    places_reservees = models.PositiveIntegerField(default=1)  # Nombre de places réservées
    montant_reservation=models.DecimalField(max_digits=10, decimal_places=2 , default=0)
    datereservation = models.DateTimeField(auto_now_add=True)  # Date de la réservation
    dateupdate=models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.numero_reservation:
            # Génère un numéro de réservation unique basé sur l'ID du trajet et un UUID
            annee_courante = datetime.datetime.now().year
            self.numero_reservation = f"TICKET-{annee_courante}-{self.voyage.id}-{uuid.uuid4().hex[:6].upper()}"    
                
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client} -> {self.voyage}"
    
class Payement(models.Model):
    reservation=models.OneToOneField(Reservation, on_delete=models.PROTECT)
    montant=models.DecimalField(max_digits=10, decimal_places=2)
    modepayement=models.CharField(max_length=100)
    reference=models.CharField(max_length=100)
    numeropayement=models.CharField(max_length=100)
    datepayement=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reservation} -> {self.montant}"

