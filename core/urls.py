from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/creer/', views.creer_utilisateur, name='creer_utilisateur'),
    path('roles/', views.liste_roles, name='liste_roles'),
    path('roles/creer/', views.creer_role, name='creer_role'),
    
    # URLs pour les catégories
    path('categories/', views.CategorieListView.as_view(), name='liste_categories'),
    path('categories/creer/', views.CategorieCreateView.as_view(), name='creer_categorie'),
    path('categories/<int:pk>/modifier/', views.CategorieUpdateView.as_view(), name='modifier_categorie'),
    path('categories/<int:pk>/supprimer/', views.CategorieDeleteView.as_view(), name='supprimer_categorie'),
    
    # URLs pour les fournisseurs
    path('fournisseurs/', views.FournisseurListView.as_view(), name='liste_fournisseurs'),
    path('fournisseurs/creer/', views.FournisseurCreateView.as_view(), name='creer_fournisseur'),
    path('fournisseurs/<int:pk>/modifier/', views.FournisseurUpdateView.as_view(), name='modifier_fournisseur'),
    path('fournisseurs/<int:pk>/supprimer/', views.FournisseurDeleteView.as_view(), name='supprimer_fournisseur'),
    
    # URLs pour les articles
    path('articles/', views.ArticleListView.as_view(), name='liste_articles'),
    path('articles/creer/', views.creer_article, name='creer_article'),
    path('articles/<int:pk>/modifier/', views.ArticleUpdateView.as_view(), name='modifier_article'),
    path('articles/<int:pk>/supprimer/', views.ArticleDeleteView.as_view(), name='supprimer_article'),

    # URLs pour les commandes
    path('commandes/', views.liste_commandes, name='liste_commandes'),
    path('commandes/nouvelle/', views.nouvelle_commande, name='nouvelle_commande'),
    path('commandes/<int:pk>/', views.detail_commande, name='detail_commande'),
    path('commandes/<int:pk>/confirmer/', views.confirmer_commande, name='confirmer_commande'),
    path('commandes/<int:pk>/annuler/', views.annuler_commande, name='annuler_commande'),
    path('commandes/<int:pk>/recu/', views.recu_commande, name='recu_commande'),
    
    # URLs pour la gestion des stocks
    path('stock/', views.gestion_stock, name='gestion_stock'),
    path('stock/mouvements/', views.mouvements_stock, name='mouvements_stock'),
    path('stock/entrees/', views.entrees_stock, name='entrees_stock'),
    path('stock/sorties/', views.sorties_stock, name='sorties_stock'),
    path('stock/corrections/', views.corrections_stock, name='corrections_stock'),
    path('api/fournisseur/<int:fournisseur_id>/stats/', views.fournisseur_stats, name='fournisseur_stats'),
    path('api/article/<int:article_id>/prix/', views.get_article_price, name='get_article_price'),

    # URLs pour les factures
    path('factures/', views.liste_factures, name='liste_factures'),
    path('factures/<int:pk>/', views.detail_facture, name='detail_facture'),
] 