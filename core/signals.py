from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Commande, Facture

@receiver(post_save, sender=Commande)
def creer_facture(sender, instance, created, **kwargs):
    """
    Signal qui crée automatiquement une facture lorsqu'une commande est confirmée
    """
    if instance.statut == 'confirmee' and not hasattr(instance, 'facture'):
        Facture.objects.create(
            commande=instance,
            total_ht=instance.total_ht,
            total_ttc=instance.total_ttc
        ) 