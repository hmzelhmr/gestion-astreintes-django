from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    #--------utilisateurs--------
    path('login/', views.login_admin, name="login_admin"),
    path('signup/', views.signup_admin, name="signup_admin"),
    path('dashboard/', views.dashboard_admin, name="dashboard_admin"),
    path('logout/', views.logout_admin, name="logout_admin"),

    path('login_secretaire/', views.login_secretaire, name="login_secretaire"),
    path('signup_secretaire/', views.signup_secretaire, name="signup_secretaire"),
    path('dashboard_secretaire/', views.dashboard_secretaire, name="dashboard_secretaire"),
    path('logout_secretaire/', views.logout_secretaire, name="logout_secretaire"),
    
    path('collaborateur/add/', views.add_collaborateur, name="add_collaborateur"),
    
    path('collaborateur/login/', views.login_collaborateur, name="login_collaborateur"),
    path('collaborateur/dashboard/', views.dashboard_collaborateur, name="dashboard_collaborateur"),
    path("collaborateur/list/", views.list_collaborateurs, name="list_collaborateurs"),
    path("collaborateur/edit/<str:matricule>/", views.edit_collaborateur, name="edit_collaborateur"),
    path("collaborateur/delete/<str:matricule>/", views.delete_collaborateur, name="delete_collaborateur"),
    path('collaborateur/logout/', views.logout_collaborateur, name="logout_collaborateur"),
    
    path('chef/login/', views.login_chef, name="login_chef"),
    path('chef/dashboard/', views.dashboard_chef, name="dashboard_chef"),
    path('chef/logout/', views.logout_chef, name="logout_chef"),
    path('chef/add/', views.add_chef, name="add_chef"),
    path('chef/edit/<int:chef_id>/', views.edit_chef, name="edit_chef"),
    path('chef/delete/<int:chef_id>/', views.delete_chef, name="delete_chef"),
    path('services/list/', views.list_services, name="list_services"),
    path('services/add/', views.add_service, name="add_service"),
    path('services/edit/<int:service_id>/', views.edit_service, name="edit_service"),
    path('services/delete/<int:service_id>/', views.delete_service, name="delete_service"),

    path("collaborateur/indisponibilites/", views.mes_indisponibilites, name="mes_indisponibilites"),
    path("collaborateur/indisponibilites/add/", views.add_indisponibilite, name="add_indisponibilite"),

    # Admin / Secretaire
    path("indisponibilites/", views.list_indisponibilites, name="list_indisponibilites"),
    path("indisponibilites/<int:id_indisponibilite>/<str:action>/", views.changer_statut_indisponibilite, name="changer_statut_indisponibilite"),
    path("planning_weekend/", views.planning_weekend, name="planning_weekend"),
    path("generer_planning_weekend/", views.generer_planning_weekend, name="generer_planning_weekend"),
    path("stratégie/", views.strategie, name="strategie"),
    path("a_propos/", views.a_propos, name="a_propos"),
    path("gestion_utilisateurs/", views.gestion_utilisateurs, name="gestion_utilisateurs"),
    path("gestion_utilisateurs_secretaire/", views.gestion_utilisateurs_secretaire, name="gestion_utilisateurs_secretaire"),
    path("chefservice/", views.ChefService, name="chefservice"),
    path("planning/<int:planning_id>/pdf/", views.exporter_planning_pdf, name="exporter_planning_pdf"),
    path("planning/<int:planning_id>/excel/", views.exporter_planning_excel, name="exporter_planning_excel"),
    path("password_reset/", views.password_reset_request, name="password_reset_request"),
    path("password_reset/verify/", views.password_reset_verify, name="password_reset_verify"),
]
