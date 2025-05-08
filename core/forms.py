from django import forms
from django.forms import inlineformset_factory
from .models import Commande, LigneCommande, MouvementStock, Article, ArticleNumeroSerie

class CommandeForm(forms.ModelForm):
    class Meta:
        model = Commande
        fields = ['fournisseur', 'date_livraison_prevue', 'notes']
        widgets = {
            'date_livraison_prevue': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class LigneCommandeForm(forms.ModelForm):
    class Meta:
        model = LigneCommande
        fields = ['article', 'quantite']
        widgets = {
            'article': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['article'].queryset = Article.objects.all()
        self.fields['article'].label_from_instance = lambda obj: f"{obj.nom} (Prix d'achat: {obj.prix_achat}€)"
        
        # Ajouter le prix d'achat comme attribut data pour chaque option
        self.fields['article'].widget.attrs['data-prix-achat'] = ''
        for article in self.fields['article'].queryset:
            self.fields['article'].widget.attrs[f'data-prix-achat-{article.id}'] = str(article.prix_achat)

LigneCommandeFormSet = inlineformset_factory(
    Commande, LigneCommande,
    form=LigneCommandeForm,
    extra=1,
    can_delete=True
)

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['nom', 'description', 'categorie', 'fournisseur', 'prix_achat', 'prix_vente', 'seuil_alerte']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'prix_achat': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'prix_vente': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'seuil_alerte': forms.NumberInput(attrs={'min': '0'}),
        }

class ArticleNumeroSerieForm(forms.ModelForm):
    class Meta:
        model = ArticleNumeroSerie
        fields = ['numero_serie', 'date_acquisition']
        widgets = {
            'date_acquisition': forms.DateInput(attrs={'type': 'date'}),
        }

ArticleNumeroSerieFormSet = inlineformset_factory(
    MouvementStock,
    ArticleNumeroSerie,
    form=ArticleNumeroSerieForm,
    extra=1,
    can_delete=True,
    fk_name='mouvement'
)

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['article', 'quantite', 'motif']
        widgets = {
            'quantite': forms.NumberInput(attrs={'min': '1'}),
            'motif': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fournisseur'].required = False 