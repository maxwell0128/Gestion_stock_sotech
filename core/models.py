from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

class Role(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    permissions = models.JSONField(default=dict)

    def __str__(self):
        return self.nom

class Utilisateur(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    telephone = models.CharField(max_length=15, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    # Ajout des related_name pour résoudre les conflits
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utilisateur_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utilisateur_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return self.username

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=15)
    email = models.EmailField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    def get_commandes_recentes(self, limit=5):
        """Récupère les commandes récentes du fournisseur"""
        return self.commande_set.all().order_by('-date_commande')[:limit]

    def get_total_commandes(self):
        """Calcule le montant total des commandes"""
        return self.commande_set.aggregate(total=models.Sum('total_ttc'))['total'] or 0

class Article(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    seuil_alerte = models.IntegerField(default=10, help_text="Seuil d'alerte pour le réapprovisionnement")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom

    def get_numeros_serie(self):
        return ArticleNumeroSerie.objects.filter(article=self)

class ArticleNumeroSerie(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    mouvement = models.ForeignKey('MouvementStock', on_delete=models.CASCADE, null=True, blank=True)
    numero_serie = models.CharField(max_length=100, unique=True)
    date_acquisition = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.article.nom} - {self.numero_serie}"

# Nouveaux modèles pour les commandes et la gestion des stocks
class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('en_cours', 'En cours de livraison'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]
    
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, null=True, blank=True)
    date_commande = models.DateTimeField(auto_now_add=True)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    date_livraison_reelle = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    notes = models.TextField(blank=True)
    total_ht = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande {self.id} - {self.fournisseur.nom} ({self.get_statut_display()})"
    
    def calculer_totaux(self):
        total_ht = sum(ligne.prix_unitaire * ligne.quantite for ligne in self.lignes.all())
        self.total_ht = total_ht
        self.total_ttc = total_ht * Decimal('1.20')  # TVA à 20% en utilisant Decimal
        self.save()

    @property
    def montant_tva(self):
        """Calcule le montant de la TVA (TTC - HT)"""
        return self.total_ttc - self.total_ht

    def save(self, *args, **kwargs):
        if not self.date_livraison_prevue:
            # Définir la date de livraison prévue à 7 jours après la commande
            self.date_livraison_prevue = timezone.now().date() + timedelta(days=7)
        super().save(*args, **kwargs)

class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.article.nom} x {self.quantite}"

    def save(self, *args, **kwargs):
        if not self.prix_unitaire:
            # Utiliser le prix d'achat de l'article comme prix unitaire par défaut
            self.prix_unitaire = self.article.prix_achat
        super().save(*args, **kwargs)

    @property
    def total(self):
        """Calcule le total de la ligne (prix unitaire × quantité)"""
        return self.prix_unitaire * self.quantite

class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entrée'),
        ('SORTIE', 'Sortie'),
        ('CORRECTION', 'Correction'),
    ]

    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    motif = models.TextField()
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"

    def __str__(self):
        return f"{self.get_type_display()} de {self.quantite} {self.article.nom} le {self.date}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Facture(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente de paiement'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='facture')
    numero = models.CharField(max_length=50, unique=True)
    date_emission = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    total_ht = models.DecimalField(max_digits=10, decimal_places=2)
    total_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Facture {self.numero} - {self.commande.fournisseur.nom}"

    def save(self, *args, **kwargs):
        if not self.numero:
            # Générer un numéro de facture unique
            self.numero = f"FAC-{timezone.now().strftime('%Y%m%d')}-{self.commande.id:04d}"
        if not self.date_echeance:
            # Définir la date d'échéance à 30 jours après l'émission
            self.date_echeance = timezone.now().date() + timedelta(days=30)
        super().save(*args, **kwargs)

    @property
    def montant_tva(self):
        """Calcule le montant de la TVA (TTC - HT)"""
        return self.total_ttc - self.total_ht
