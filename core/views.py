from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utilisateur, Role, Categorie, Fournisseur, Article, ArticleNumeroSerie, Commande, LigneCommande, MouvementStock, Facture
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .forms import CommandeForm, LigneCommandeFormSet, MouvementStockForm, ArticleForm, ArticleNumeroSerieFormSet
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Count, Sum, Max
from django.utils import timezone
from datetime import datetime

# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

@login_required
def liste_utilisateurs(request):
    utilisateurs = Utilisateur.objects.all()
    return render(request, 'core/utilisateurs.html', {'utilisateurs': utilisateurs})

@login_required
def liste_roles(request):
    roles = Role.objects.all()
    return render(request, 'core/roles.html', {'roles': roles})

@login_required
def creer_utilisateur(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role_id = request.POST.get('role')
        telephone = request.POST.get('telephone')

        try:
            # Vérifier si l'utilisateur existe déjà
            if Utilisateur.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
                return redirect('creer_utilisateur')

            # Créer le nouvel utilisateur
            utilisateur = Utilisateur.objects.create_user(
                username=username,
                email=email,
                password=password,
                telephone=telephone
            )

            # Assigner le rôle si spécifié
            if role_id:
                try:
                    role = Role.objects.get(id=role_id)
                    utilisateur.role = role
                    utilisateur.save()
                except Role.DoesNotExist:
                    messages.warning(request, 'Le rôle spécifié n\'existe pas.')

            messages.success(request, 'Utilisateur créé avec succès')
            return redirect('liste_utilisateurs')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création de l\'utilisateur : {str(e)}')
            return redirect('creer_utilisateur')

    # Récupérer la liste des rôles pour le formulaire
    roles = Role.objects.all()
    return render(request, 'core/creer_utilisateur.html', {'roles': roles})

@login_required
def creer_role(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        permissions = request.POST.getlist('permissions')  # Récupère la liste des permissions cochées

        try:
            # Vérifier si le rôle existe déjà
            if Role.objects.filter(nom=nom).exists():
                messages.error(request, 'Ce nom de rôle est déjà pris.')
                return redirect('creer_role')

            # Créer le nouveau rôle
            role = Role.objects.create(
                nom=nom,
                description=description,
                permissions={'permissions': permissions}  # Stocke les permissions dans le champ JSON
            )

            messages.success(request, 'Rôle créé avec succès')
            return redirect('liste_roles')
        except Exception as e:
            messages.error(request, f'Erreur lors de la création du rôle : {str(e)}')
            return redirect('creer_role')

    return render(request, 'core/creer_role.html')

# Nouvelles vues pour les catégories
class CategorieListView(LoginRequiredMixin, ListView):
    model = Categorie
    template_name = 'core/categories/liste.html'
    context_object_name = 'categories'

class CategorieCreateView(LoginRequiredMixin, CreateView):
    model = Categorie
    template_name = 'core/categories/creer.html'
    fields = ['nom', 'description']
    success_url = reverse_lazy('liste_categories')

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie créée avec succès')
        return super().form_valid(form)

class CategorieUpdateView(LoginRequiredMixin, UpdateView):
    model = Categorie
    template_name = 'core/categories/modifier.html'
    fields = ['nom', 'description']
    success_url = reverse_lazy('liste_categories')

    def form_valid(self, form):
        messages.success(self.request, 'Catégorie modifiée avec succès')
        return super().form_valid(form)

class CategorieDeleteView(LoginRequiredMixin, DeleteView):
    model = Categorie
    template_name = 'core/categories/supprimer.html'
    success_url = reverse_lazy('liste_categories')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Catégorie supprimée avec succès')
        return super().delete(request, *args, **kwargs)

# Vues pour les fournisseurs
class FournisseurListView(LoginRequiredMixin, ListView):
    model = Fournisseur
    template_name = 'core/fournisseurs/liste.html'
    context_object_name = 'fournisseurs'

class FournisseurCreateView(LoginRequiredMixin, CreateView):
    model = Fournisseur
    template_name = 'core/fournisseurs/creer.html'
    fields = ['nom', 'adresse', 'telephone', 'email']
    success_url = reverse_lazy('liste_fournisseurs')

    def form_valid(self, form):
        messages.success(self.request, 'Fournisseur créé avec succès')
        return super().form_valid(form)

class FournisseurUpdateView(LoginRequiredMixin, UpdateView):
    model = Fournisseur
    template_name = 'core/fournisseurs/modifier.html'
    fields = ['nom', 'adresse', 'telephone', 'email']
    success_url = reverse_lazy('liste_fournisseurs')

    def form_valid(self, form):
        messages.success(self.request, 'Fournisseur modifié avec succès')
        return super().form_valid(form)

class FournisseurDeleteView(LoginRequiredMixin, DeleteView):
    model = Fournisseur
    template_name = 'core/fournisseurs/supprimer.html'
    success_url = reverse_lazy('liste_fournisseurs')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Fournisseur supprimé avec succès')
        return super().delete(request, *args, **kwargs)

# Vues pour les articles
class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'core/articles/liste.html'
    context_object_name = 'articles'

@login_required
def creer_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            messages.success(request, 'Article créé avec succès')
            return redirect('liste_articles')
        else:
            messages.error(request, 'Erreur lors de la création de l\'article')
    else:
        form = ArticleForm()
    
    return render(request, 'core/articles/creer.html', {'form': form})

class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'core/articles/modifier.html'
    success_url = reverse_lazy('liste_articles')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Article modifié avec succès')
        return response

class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = 'core/articles/supprimer.html'
    success_url = reverse_lazy('liste_articles')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Article supprimé avec succès')
        return super().delete(request, *args, **kwargs)

@login_required
def liste_commandes(request):
    commandes = Commande.objects.all().order_by('-date_commande')
    return render(request, 'core/commandes/liste.html', {'commandes': commandes})

@login_required
def liste_factures(request):
    factures = Facture.objects.all().order_by('-date_emission')
    return render(request, 'core/factures/liste.html', {'factures': factures})

@login_required
def detail_facture(request, pk):
    facture = get_object_or_404(Facture, pk=pk)
    return render(request, 'core/factures/detail.html', {'facture': facture})

@login_required
def detail_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    facture = getattr(commande, 'facture', None)  # Récupère la facture associée si elle existe
    return render(request, 'core/commandes/detail.html', {
        'commande': commande,
        'facture': facture
    })

@login_required
def nouvelle_commande(request):
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        formset = LigneCommandeFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            commande = form.save(commit=False)
            commande.utilisateur = request.user  # Ajout de l'utilisateur
            commande.save()
            formset.instance = commande
            lignes = formset.save(commit=False)
            for ligne in lignes:
                ligne.prix_unitaire = ligne.article.prix_achat
                ligne.save()
            formset.save_m2m()
            commande.calculer_totaux()
            
            # Création automatique de la facture
            if commande.statut == 'confirmee':
                Facture.objects.create(
                    commande=commande,
                    total_ht=commande.total_ht,
                    total_ttc=commande.total_ttc
                )
            
            messages.success(request, 'Commande créée avec succès.')
            return redirect('detail_commande', pk=commande.pk)
    else:
        form = CommandeForm()
        formset = LigneCommandeFormSet()
    return render(request, 'core/commandes/form.html', {
        'form': form,
        'formset': formset,
        'titre': 'Nouvelle Commande'
    })

@login_required
def mouvement_stock(request):
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save()
            messages.success(request, 'Mouvement de stock enregistré avec succès.')
            return redirect('liste_mouvements')
    else:
        form = MouvementStockForm()
    return render(request, 'core/stock/mouvement.html', {'form': form})

@login_required
def liste_mouvements(request):
    mouvements = MouvementStock.objects.all().order_by('-date')
    return render(request, 'core/stock/liste.html', {'mouvements': mouvements})

@login_required
def etat_stock(request):
    articles = Article.objects.all()
    return render(request, 'core/stock/etat.html', {'articles': articles})

@login_required
def gestion_stock(request):
    return render(request, 'core/stock/index.html')

@login_required
def mouvements_stock(request):
    mouvements = MouvementStock.objects.all().order_by('-date')
    return render(request, 'core/stock/mouvements.html', {'mouvements': mouvements})

@login_required
def entrees_stock(request):
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        formset = ArticleNumeroSerieFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                mouvement = form.save(commit=False)
                mouvement.type = 'ENTREE'
                mouvement.utilisateur = request.user
                
                # Vérification que la quantité est positive
                if mouvement.quantite <= 0:
                    messages.error(request, 'La quantité doit être positive pour une entrée de stock.')
                    return redirect('entrees_stock')
                
                # Vérification que le nombre de numéros de série correspond à la quantité
                numeros_serie_valides = [f for f in formset if f.cleaned_data and not f.cleaned_data.get('DELETE', False)]
                if len(numeros_serie_valides) != mouvement.quantite:
                    messages.error(request, f'Le nombre de numéros de série ({len(numeros_serie_valides)}) doit correspondre à la quantité entrée ({mouvement.quantite}).')
                    return redirect('entrees_stock')
                
                # Sauvegarde du mouvement
                mouvement.save()
                
                # Sauvegarde des numéros de série
                for form_serie in numeros_serie_valides:
                    numero_serie = form_serie.save(commit=False)
                    numero_serie.article = mouvement.article
                    numero_serie.mouvement = mouvement
                    numero_serie.save()
                
                messages.success(request, f'Entrée de {mouvement.quantite} {mouvement.article.nom} enregistrée avec succès.')
                return redirect('entrees_stock')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erreur dans le champ {field}: {error}')
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Erreur dans le numéro de série: {error}')
    else:
        form = MouvementStockForm()
        formset = ArticleNumeroSerieFormSet()
    
    entrees = MouvementStock.objects.filter(type='ENTREE').order_by('-date')
    articles = Article.objects.all().order_by('nom')
    fournisseurs = Fournisseur.objects.all().order_by('nom')
    context = {
        'form': form,
        'formset': formset,
        'entrees': entrees,
        'articles': articles,
        'fournisseurs': fournisseurs,
    }
    return render(request, 'core/stock/entrees.html', context)

@login_required
def sorties_stock(request):
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.type = 'SORTIE'
            mouvement.utilisateur = request.user
            
            # Vérification que la quantité est positive
            if mouvement.quantite <= 0:
                messages.error(request, 'La quantité doit être positive pour une sortie de stock.')
                return redirect('sorties_stock')
            
            try:
                mouvement.save()
                messages.success(request, f'Sortie de {mouvement.quantite} {mouvement.article.nom} enregistrée avec succès.')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
            return redirect('sorties_stock')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez vérifier les informations.')
    
    sorties = MouvementStock.objects.filter(type='SORTIE').order_by('-date')
    articles = Article.objects.all().order_by('nom')
    return render(request, 'core/stock/sorties.html', {
        'sorties': sorties,
        'articles': articles,
        'form': MouvementStockForm()
    })

@login_required
def corrections_stock(request):
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.type = 'CORRECTION'
            mouvement.utilisateur = request.user
            
            try:
                mouvement.save()
                messages.success(request, f'Correction de stock de {mouvement.article.nom} enregistrée avec succès.')
            except Exception as e:
                messages.error(request, f'Erreur lors de l\'enregistrement : {str(e)}')
            return redirect('corrections_stock')
        else:
            messages.error(request, 'Erreur dans le formulaire. Veuillez vérifier les informations.')
    
    corrections = MouvementStock.objects.filter(type='CORRECTION').order_by('-date')
    articles = Article.objects.all().order_by('nom')
    return render(request, 'core/stock/corrections.html', {
        'corrections': corrections,
        'articles': articles,
        'form': MouvementStockForm()
    })

@login_required
def fournisseur_stats(request, fournisseur_id):
    try:
        fournisseur = Fournisseur.objects.get(pk=fournisseur_id)
        commandes = Commande.objects.filter(fournisseur=fournisseur)
        
        # Calculer les statistiques
        nb_commandes = commandes.count()
        derniere_commande = commandes.order_by('-date_commande').first()
        total_commandes = commandes.aggregate(total=Sum('total_ttc'))['total'] or 0
        
        # Récupérer les commandes récentes
        commandes_recentes = commandes.order_by('-date_commande')[:5]
        commandes_recentes_list = []
        for commande in commandes_recentes:
            commandes_recentes_list.append({
                'id': commande.id,
                'date_commande': commande.date_commande.strftime('%d/%m/%Y'),
                'statut': commande.statut,
                'statut_display': commande.get_statut_display(),
                'total_ttc': float(commande.total_ttc)
            })
        
        data = {
            'nb_commandes': nb_commandes,
            'derniere_commande': derniere_commande.date_commande.strftime('%d/%m/%Y') if derniere_commande else None,
            'total_commandes': f"{total_commandes:.2f}",
            'commandes_recentes': commandes_recentes_list
        }
        
        return JsonResponse(data)
    except Fournisseur.DoesNotExist:
        return JsonResponse({'error': 'Fournisseur non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_article_price(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
        return JsonResponse({
            'prix_achat': float(article.prix_achat)
        })
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article non trouvé'}, status=404)

@login_required
def confirmer_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    commande.statut = 'confirmee'
    commande.save()
    # Créer la facture si elle n'existe pas déjà
    if not hasattr(commande, 'facture'):
        Facture.objects.create(
            commande=commande,
            total_ht=commande.total_ht,
            total_ttc=commande.total_ttc
        )
    return redirect('recu_commande', pk=commande.pk)

@login_required
def annuler_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    commande.delete()
    messages.success(request, 'Commande annulée et supprimée avec succès.')
    return redirect('liste_commandes')

@login_required
def recu_commande(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    return render(request, 'core/commandes/recu.html', {'commande': commande})
