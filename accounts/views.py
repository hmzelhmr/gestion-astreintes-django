from .models import Admin
from .models import Secretaire 
from .models import Collaborateur
from .models import Service
from .models import ChefService
from .models import Indisponibilite
from .models import PlanningWeekend 
from .models import PasswordResetCode
from django.db.models import Q
from .models import Garde
from datetime import date, timedelta
from django.contrib.sessions.models import Session 
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password 
from django.db.models import Case, When, Value, IntegerField
from django.contrib import messages
from datetime import datetime
from django.db import transaction
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
import io ,random
import pandas as pd
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings

def home(request):
    return render(request, "home.html")

def _add_tagged_message(request, level, text, tag):
    """
    Helper to add a message with a specific extra_tag so that templates/pages
    can filter/display messages linked to a particular page or flow.
    Usage: _add_tagged_message(request, messages.SUCCESS, "OK", "login_admin")
    """
    messages.add_message(request, level, text, extra_tags=tag)

def login_admin(request):
    if request.method == "POST":
        identifier = request.POST.get('username')  # peut être username ou email
        found = Admin.objects.filter(Q(username=identifier) | Q(email=identifier)).first()
        username = found.username if found else identifier
        password = request.POST.get('password')

        try:
            admin = Admin.objects.get(username=username)
            if check_password(password, admin.password):
                request.session['admin_id'] = admin.id
                _add_tagged_message(request, messages.SUCCESS, f"Bienvenue {admin.username} 👋", "login_admin")
                return redirect('dashboard_admin')
            else:
                _add_tagged_message(request, messages.ERROR, "❌ Mot de passe incorrect.", "login_admin")
        except Admin.DoesNotExist:
            _add_tagged_message(request, messages.ERROR, "❌ Utilisateur introuvable.", "login_admin")

    return render(request, 'login_admin.html')

def login_secretaire(request):
    if request.method == "POST":
        identifier = request.POST.get('username')
        found = Secretaire.objects.filter(Q(username=identifier) | Q(email=identifier)).first()
        username = found.username if found else identifier
        password = request.POST.get('password')

        try:
            secretaire = Secretaire.objects.get(username=username)
            if check_password(password, secretaire.password):
                request.session['secretaire_id'] = secretaire.id
                _add_tagged_message(request, messages.SUCCESS, f"Bienvenue {secretaire.username} 👋", "login_secretaire")
                return redirect('dashboard_secretaire')
            else:
                _add_tagged_message(request, messages.ERROR, "❌ Mot de passe incorrect", "login_secretaire")
        except Secretaire.DoesNotExist:
            _add_tagged_message(request, messages.ERROR, "❌ Utilisateur introuvable", "login_secretaire")

    return render(request, 'login_secretaire.html')

def login_collaborateur(request):
    if request.method == "POST":
        matricule = request.POST.get("matricule")

        try:
            collab = Collaborateur.objects.get(matricule=matricule)
            request.session["collaborateur_id"] = collab.matricule
            _add_tagged_message(request, messages.SUCCESS, f"Bienvenue {collab.nom} {collab.prenom} 👋", "login_collaborateur")
            return redirect("dashboard_collaborateur")
        except Collaborateur.DoesNotExist:
            _add_tagged_message(request, messages.ERROR, "❌ Matricule introuvable", "login_collaborateur")
    
    return render(request, "login_collaborateur.html")

def login_chef(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        chef = ChefService.objects.filter(Q(username=username) | Q(email=username)).first()

        if chef:
            if check_password(password, chef.password):
                # ✅ Stocker l’ID du chef en session
                request.session["chef_id"] = chef.id
                request.session["last_login"] = str(datetime.now().strftime("%d/%m/%Y %H:%M"))
                
                _add_tagged_message(request, messages.SUCCESS, f"Bienvenue {chef.username} 👋", "login_chef")
                return redirect("dashboard_chef")
            else:
                _add_tagged_message(request, messages.ERROR, "❌ Mot de passe incorrect.", "login_chef")
        else:
            _add_tagged_message(request, messages.ERROR, "❌ Aucun compte trouvé avec cet identifiant.", "login_chef")

    context = {
        "last_login": request.session.get("last_login"),
    }
    return render(request, "login_chef.html", context)

def signup_admin(request):

    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = make_password(request.POST['password'])

        if Admin.objects.filter(username=username).exists():
            _add_tagged_message(request, messages.ERROR, f"Le nom d'utilisateur {username} existe déjà.", "signup_admin")
            return render(request, 'signup_admin.html')
        else:
            Admin.objects.create(username=username, email=email, password=password)
            _add_tagged_message(request, messages.SUCCESS, "Compte administrateur créé. Vous pouvez vous connecter.", "signup_admin")
            return redirect('login_admin')

    return render(request, 'signup_admin.html')

def signup_secretaire(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = make_password(request.POST['password'])

        if Secretaire.objects.filter(username=username).exists():
            _add_tagged_message(request, messages.ERROR, f"Le nom d'utilisateur {username} existe déjà.", "signup_secretaire")
            return render(request, 'signup_secretaire.html')
        else:
            Secretaire.objects.create(username=username, email=email, password=password)
            _add_tagged_message(request, messages.SUCCESS, "Compte secrétaire créé. Vous pouvez vous connecter.", "signup_secretaire")
            return redirect('login_secretaire')

    return render(request, 'signup_secretaire.html')

def dashboard_admin(request):
    if 'admin_id' not in request.session:
        return redirect('login_admin')
    
    try:
        admin = Admin.objects.get(id=request.session['admin_id'])
    except Admin.DoesNotExist:
        request.session.flush()
        return redirect('login_admin')

    collaborateurs_count = Collaborateur.objects.count()
    chefs_count = ChefService.objects.count()
    services_count = Service.objects.count()

    active_sessions_qs = Session.objects.filter(expire_date__gte=timezone.now())
    total_active_sessions = active_sessions_qs.count()
    session_user_counts = {"admins": 0, "secretaires": 0, "collaborateurs": 0, "chefs": 0}
    for s in active_sessions_qs:
        data = s.get_decoded()
        if "admin_id" in data:
            session_user_counts["admins"] += 1
        if "secretaire_id" in data:
            session_user_counts["secretaires"] += 1
        if "collaborateur_id" in data:
            session_user_counts["collaborateurs"] += 1
        if "chef_id" in data:
            session_user_counts["chefs"] += 1

    admin.collaborateurs_count = collaborateurs_count
    admin.chefs_count = chefs_count
    admin.services_count = services_count
    admin.total_active_sessions = total_active_sessions
    admin.session_user_counts = session_user_counts
    indispo = Indisponibilite.objects.filter(statut='en_attente')
    pending_count = indispo.count()
    admin.pending_count = pending_count
    return render(request, 'dashboard_admin.html', {"admin": admin, "indisponibilites": indispo})

def dashboard_secretaire(request):
    if 'secretaire_id' not in request.session:
        return redirect('login_secretaire')

    try:
        secretaire = Secretaire.objects.get(id=request.session['secretaire_id'])
    except Secretaire.DoesNotExist:
        request.session.flush()
        return redirect('login_secretaire')

    collaborateurs_count = Collaborateur.objects.count()

    active_sessions_qs = Session.objects.filter(expire_date__gte=timezone.now())
    active_collab_sessions = 0
    for s in active_sessions_qs:
        data = s.get_decoded()
        if "collaborateur_id" in data:
            active_collab_sessions += 1

    indispo = Indisponibilite.objects.filter(statut='en_attente')
    pending_count = indispo.count()

    secretaire.collaborateurs_count = collaborateurs_count
    secretaire.active_collab_sessions_count = active_collab_sessions
    secretaire.pending_count = pending_count

    return render(request, 'dashboard_secretaire.html', {"secretaire": secretaire, "indisponibilites": indispo})

def dashboard_collaborateur(request):
    if "collaborateur_id" not in request.session:
        return redirect("login_collaborateur")

    matricule = request.session["collaborateur_id"]

    try:
        c = Collaborateur.objects.get(matricule=matricule)
    except Collaborateur.DoesNotExist:
        return redirect("login_collaborateur")

    return render(request, "dashboard_collaborateur.html", {"c": c})

def dashboard_chef(request):
    chef_id = request.session.get("chef_id")
    chef = get_object_or_404(ChefService, id=chef_id)

    service = chef.service

    collaborateurs = []
    if service:
        collaborateurs = service.collaborateur_set.all()

    return render(request, "dashboard_chef.html", {
        "chef": chef,
        "service": service,
        "collaborateurs": collaborateurs
    })

def logout_admin(request):
    request.session.flush()
    return redirect('login_admin')

def logout_secretaire(request):
    request.session.flush()
    return redirect('login_secretaire')

def logout_collaborateur(request):
    try:
        del request.session["collaborateur_id"]
    except KeyError:
        pass
    return redirect("login_collaborateur")

def logout_chef(request):
    request.session.flush()
    return redirect("login_chef")

def list_collaborateurs(request):
    collaborateurs = Collaborateur.objects.select_related('service').all()
    services = Service.objects.all().values('id_service', 'nom_service', 'chef')
    for collab in collaborateurs:
        collab.refresh_from_db() 
    
    if request.session.get("admin_id"):
        return render(request, "gestion_utilisateurs.html", {
            "collaborateurs": collaborateurs,
            "services": services
        })
    elif request.session.get("secretaire_id"):
        return render(request, "gestion_utilisateurs_secretaire.html", {
            "collaborateurs": collaborateurs,
            "services": services
        })
    else:
        return redirect("home")

def chefservice(request):
    if 'admin_id' not in request.session and 'secretaire_id' not in request.session:
        return redirect('login_admin')

    chefservice = ChefService.objects.select_related('service').all().order_by('nom', 'prenom')
     
    if request.session.get("admin_id"):
        return render(request, "gestion_utilisateurs.html", {"chefservice": chefservice})
    elif request.session.get("secretaire_id"):
        return render(request, "gestion_utilisateurs_secretaire.html", {"chefservice": chefservice})
    else:
        return render(request, "home.html", {"chefservice": chefservice})

def add_chef(request):
    if 'admin_id' not in request.session:
        return redirect('login_admin')

    services = Service.objects.all()
    chefs = ChefService.objects.select_related('service').all().order_by('nom', 'prenom')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        service_id = request.POST.get('service')
        new_service_name = (request.POST.get('new_service_name') or "").strip()

        # Vérif doublons
        if ChefService.objects.filter(username=username).exists():
            _add_tagged_message(request, messages.ERROR, f"Le nom d'utilisateur {username} existe déjà.", "gestion")
            return render(request, "gestion_utilisateurs.html", {
                "services": services,
                "chefs": chefs,
                "error": f"Le nom d'utilisateur {username} existe déjà."
            })

        if ChefService.objects.filter(email=email).exists():
            _add_tagged_message(request, messages.ERROR, f"L'email {email} est déjà utilisé.", "gestion")
            return render(request, "gestion_utilisateurs.html", {
                "services": services,
                "chefs": chefs,
                "error": f"L'email {email} est déjà utilisé."
            })

        if password != confirm_password:
            _add_tagged_message(request, messages.ERROR, "Les mots de passe ne correspondent pas.", "gestion")
            return render(request, "gestion_utilisateurs.html", {
                "services": services,
                "chefs": chefs,
                "error": "Les mots de passe ne correspondent pas."
            })

        # Choix du service
        service = None
        if service_id:
            service = Service.objects.get(id_service=service_id)
        elif new_service_name:
            service, _ = Service.objects.get_or_create(nom_service=new_service_name)

        if not service:
            _add_tagged_message(request, messages.ERROR, "Vous devez sélectionner ou créer un service.", "gestion")
            return render(request, "gestion_utilisateurs.html", {
                "services": services,
                "chefs": chefs,
                "error": "Vous devez sélectionner ou créer un service."
            })

        if hasattr(service, "chef") and service.chef:
            _add_tagged_message(request, messages.ERROR, f"Le service {service.nom_service} a déjà un chef.", "gestion")
            return render(request, "gestion_utilisateurs.html", {
                "services": services,
                "chefs": chefs,
                "error": f"Le service {service.nom_service} a déjà un chef."
            })

        # Création chef
        chef = ChefService(
            username=username,
            email=email,
            nom=nom,
            prenom=prenom,
            must_change_password=True,
            service=service
        )
        chef.password = make_password(password)
        chef.save()

        _add_tagged_message(request, messages.SUCCESS, f"Chef {chef.nom} {chef.prenom} ajouté.", "gestion")
        # Après ajout, rediriger vers la liste complète
        return redirect("chefservice")

    # GET : afficher la page avec formulaire et liste
    return render(request, "gestion_utilisateurs.html", {
        "services": services,
        "chefs": chefs
    })

def list_services(request):
    services = Service.objects.all()
    chef_services = ChefService.objects.all()
    return render(request, "gestion_utilisateurs.html", {
        "services": services,
        "chef_services": chef_services
    })

def add_indisponibilite(request):
    collab_matricule = request.session.get("collaborateur_id")
    if not collab_matricule:
        return redirect("login_collaborateur")

    collab = get_object_or_404(Collaborateur, matricule=collab_matricule)

    now = timezone.now()
    prochain_samedi = now.date() + timedelta((5 - now.weekday()) % 7)
    vendredi_2359 = prochain_samedi - timedelta(days=1)
    # rendre deadline aware
    deadline_naive = datetime.combine(vendredi_2359, datetime.max.time()).replace(hour=23, minute=59, second=59)
    deadline = timezone.make_aware(deadline_naive)

    if request.method == "POST":
        date_debut_str = request.POST.get("date_debut")
        date_fin_str = request.POST.get("date_fin")
        raison = request.POST.get("raison")

        if not date_debut_str or not date_fin_str:
            _add_tagged_message(request, messages.ERROR, "⚠️ Merci de renseigner les deux dates.", "indisponibilite")
            return render(request, "add_indisponibilite.html", {"collaborateur": collab})

        # conversion des strings en datetime aware
        date_debut_naive = datetime.fromisoformat(date_debut_str)
        date_fin_naive = datetime.fromisoformat(date_fin_str)
        date_debut = timezone.make_aware(date_debut_naive)
        date_fin = timezone.make_aware(date_fin_naive)

        if now > deadline:
            _add_tagged_message(request, messages.ERROR, "❌ Vous ne pouvez plus déclarer une indisponibilité après vendredi 23h59.", "indisponibilite")
            return render(request, "add_indisponibilite.html", {"collaborateur": collab})

        if date_debut > date_fin:
            _add_tagged_message(request, messages.ERROR, "⚠️ La date de début doit être avant la date de fin.", "indisponibilite")
            return render(request, "add_indisponibilite.html", {"collaborateur": collab})

        Indisponibilite.objects.create(
            collaborateur=collab,
            date_debut=date_debut,
            date_fin=date_fin,
            raison=raison
        )
        _add_tagged_message(request, messages.SUCCESS, "✅ Indisponibilité enregistrée avec succès.", "indisponibilite")
        return render(request, "add_indisponibilite.html", {"collaborateur": collab})

    return render(request, "add_indisponibilite.html", {"collaborateur": collab})

def mes_indisponibilites(request):
    collab_matricule = request.session.get("collaborateur_id")
    if not collab_matricule:
        return redirect("login_collaborateur")

    collaborateur = get_object_or_404(Collaborateur, matricule=collab_matricule)
    indispo = Indisponibilite.objects.filter(collaborateur=collaborateur).order_by("-date_debut")

    return render(request, "mes_indisponibilites.html", {
        "collaborateur": collaborateur,
        "indisponibilites": indispo
    })

def add_collaborateur(request):
    if not (request.session.get("admin_id") or request.session.get("secretaire_id")):
        return redirect("login_admin")

    services = Service.objects.all()
    collaborateurs = Collaborateur.objects.select_related("service").all().order_by("nom", "prenom")

    if request.method == "POST":
        matricule = request.POST.get("matricule")
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        email = request.POST.get("email")
        telephone = request.POST.get("telephone")
        service_id = request.POST.get("service")

        if service_id and not Collaborateur.objects.filter(matricule=matricule).exists():
            if request.session.get("admin_id"):
                added_by = Admin.objects.get(id=request.session["admin_id"])
            else:
                added_by = Secretaire.objects.get(id=request.session["secretaire_id"])

            try:
                service = Service.objects.get(id_service=service_id)
                Collaborateur.objects.create(
                    matricule=matricule,
                    nom=nom,
                    prenom=prenom,
                    email=email,
                    telephone=telephone,
                    service=service,
                    added_by=added_by
                )
                _add_tagged_message(request, messages.SUCCESS, f"Collaborateur {nom} {prenom} ajouté.", "gestion")
            except Service.DoesNotExist:
                _add_tagged_message(request, messages.ERROR, "Service introuvable.", "gestion")
                pass  # si service non trouvé → on ignore

        # Après ajout → recharger la même page avec les données
        return render(request, "gestion_utilisateurs.html", {
            "services": services,
            "collaborateurs": Collaborateur.objects.select_related("service").all().order_by("nom", "prenom"),
        })

    # GET → juste afficher la page avec liste vide/remplie
    return render(request, "gestion_utilisateurs.html", {
        "services": services,
        "collaborateurs": collaborateurs,
    })

def add_service(request):
    if 'admin_id' not in request.session:
        return redirect('login_admin')

    chefs = ChefService.objects.filter(service__isnull=True)  # uniquement dispo

    if request.method == "POST":
        nom_service = request.POST.get("service_nom")
        chef_id = request.POST.get("chef")
        chef_nom = request.POST.get("chef_nom")
        chef_prenom = request.POST.get("chef_prenom")
        chef_email = request.POST.get("chef_email")
        chef_username = request.POST.get("chef_username")
        chef_password = request.POST.get("chef_password")

        if Service.objects.filter(nom_service=nom_service).exists():
            _add_tagged_message(request, messages.ERROR, "Ce service existe déjà.", "gestion")
            return render(request, "gestion_utilisateurs.html", {
                "chefs": chefs,
                "error": "Ce service existe déjà."
            })

        service = Service.objects.create(nom_service=nom_service)

        if chef_id:
            chef = ChefService.objects.get(id=chef_id)
            chef.service = service
            chef.save()
        elif chef_username and chef_password:
            chef = ChefService(
                username=chef_username,
                email=chef_email,
                nom=chef_nom,
                prenom=chef_prenom,
                service=service,
                must_change_password=True
            )
            chef.password = make_password(chef_password)
            chef.save()

        _add_tagged_message(request, messages.SUCCESS, f"Service {nom_service} créé.", "gestion")
        return redirect("list_services")

    return render(request, "gestion_utilisateurs.html", {"chefs": chefs})

def edit_collaborateur(request, matricule): 
    collaborateur = Collaborateur.objects.get(matricule=matricule)
    services = Service.objects.all()

    if request.method == "POST":
        collaborateur.nom = request.POST.get("nom")
        collaborateur.prenom = request.POST.get("prenom")
        collaborateur.email = request.POST.get("email")
        collaborateur.telephone = request.POST.get("telephone")

        service_id = request.POST.get("service")
        if service_id:
            collaborateur.service = Service.objects.get(id_service=service_id)

            collaborateur.save()
            _add_tagged_message(request, messages.SUCCESS, "Collaborateur mis à jour.", "gestion")
        return redirect("list_collaborateurs")

    return render(request, "gestion_utilisateurs.html", {
        "collaborateur": collaborateur,
        "services": services
    })

def edit_service(request, service_id):
    if 'admin_id' not in request.session:
        return redirect('login_admin')

    service = get_object_or_404(Service, id_service=service_id)
    chef_service = service.chef

    if request.method == "POST":
        nom_service = request.POST.get("nom_service")
        nom_chef = request.POST.get("nom_chef")
        prenom_chef = request.POST.get("prenom_chef")

        if not nom_service:
            return redirect("list_services")

        if Service.objects.filter(nom_service=nom_service).exclude(id_service=service_id).exists():
            pass
        else:
            service.nom_service = nom_service
            service.save()

            if chef_service:
                chef_service.nom = nom_chef
                chef_service.prenom = prenom_chef
                chef_service.save()

            _add_tagged_message(request, messages.SUCCESS, "Service mis à jour.", "gestion")
            return redirect("list_services")

    return render(request, "gestion_utilisateurs.html", {"service": service})

def delete_collaborateur(request, matricule):
    collab = get_object_or_404(Collaborateur, matricule=matricule)
    collab.delete()
    _add_tagged_message(request, messages.SUCCESS, "Collaborateur supprimé.", "gestion")
    return redirect("list_collaborateurs")

def delete_service(request, service_id):
    if 'admin_id' not in request.session:
        return redirect('login_admin')

    service = get_object_or_404(Service, id_service=service_id)
    service.delete()
    _add_tagged_message(request, messages.SUCCESS, "Service supprimé.", "gestion")
    return redirect("list_services")

@require_POST
def edit_chef(request, chef_id):
    if 'admin_id' not in request.session:
        return redirect("login_admin")

    chef = get_object_or_404(ChefService, id=chef_id)
    services = Service.objects.all()

    if request.method == "POST":
        chef.username = request.POST.get("username")
        chef.nom = request.POST.get("nom")
        chef.prenom = request.POST.get("prenom")
        chef.email = request.POST.get("email")

        service_id = request.POST.get("service")
        if service_id:
            chef.service = Service.objects.get(id_service=service_id)
        else:
            chef.service = None

        chef.save()
        _add_tagged_message(request, messages.SUCCESS, "Chef de service mis à jour.", "gestion")
        return redirect("list_services")

    return render(request, "gestion_utilisateurs.html", {
        "chef": chef,
        "services": services
    })

@require_POST
# Supprimer un Chef de service
def delete_chef(request, chef_id):
    if 'admin_id' not in request.session:
        return redirect("login_admin")

    chef = get_object_or_404(ChefService, id=chef_id)
    chef.delete()
    _add_tagged_message(request, messages.SUCCESS, "Chef supprimé.", "gestion")
    return redirect("list_services")

def gestion_utilisateurs(request):
    collaborateurs = Collaborateur.objects.all()
    services = Service.objects.all()
    indispo = Indisponibilite.objects.annotate(
        priority=Case(
            When(statut='en_attente', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('priority', '-date_debut')
    chefservice = ChefService.objects.all().order_by('nom', 'prenom')
    context = {
        'collaborateurs': collaborateurs,
        'services': services,
        'indisponibilites': indispo,
        'chefservice': chefservice,
    }
    return render(request, "gestion_utilisateurs.html", context)

def gestion_utilisateurs_secretaire(request):
    collaborateurs = Collaborateur.objects.all()
    services = Service.objects.all()
    indispo = Indisponibilite.objects.annotate(
        priority=Case(
            When(statut='en_attente', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        )
    ).order_by('priority', '-date_debut')
    context = {
        'collaborateurs': collaborateurs,
        'services': services,
        'indisponibilites': indispo,
    }
    return render(request, "gestion_utilisateurs_secretaire.html", context)

#  Générer le planning du weekend
def generer_planning_weekend(start_date=None, force=False):
    today = start_date or date.today()
    prochain_samedi = today + timedelta((5 - today.weekday()) % 7)
    dimanche = prochain_samedi + timedelta(days=1)

    existing = PlanningWeekend.objects.filter(date_debut=prochain_samedi).first()
    if existing and not force:
        return existing

    with transaction.atomic():
        if existing and force:
            Garde.objects.filter(planning=existing).delete()
            existing.delete()

        planning = PlanningWeekend.objects.create(
            date_debut=prochain_samedi,
            date_fin=dimanche
        )

        for service in Service.objects.all():
            _assigner_collaborateur(planning, service, prochain_samedi, dimanche)

    # 🔹 Après génération → envoyer le planning complet
    envoyer_planning_complet(planning)

    return planning

#  Assigner collaborateur par service
def _assigner_collaborateur(planning, service, samedi, dimanche):
    candidats = Collaborateur.objects.filter(service=service).exclude(
        indisponibilite__statut="acceptee",
        indisponibilite__date_debut__lte=dimanche,
        indisponibilite__date_fin__gte=samedi
    ).order_by("nombre_gardes", "matricule")

    if not candidats.exists():
        return None

    collab = candidats.first()

    garde = Garde.objects.create(
        planning=planning,
        service=service,
        collaborateur=collab
    )

    collab.nombre_gardes = (collab.nombre_gardes or 0) + 1
    collab.save()

    # 🔹 Informer le collaborateur
    try:
        send_mail(
            "Votre garde du weekend",
            f"Bonjour {collab.prenom},\n\n"
            f"Vous êtes programmé pour la garde du service {service.nom_service} "
            f"le {samedi} et {dimanche}.\n\nMerci de votre disponibilité.",
            None,
            [collab.email]
        )
    except Exception:
        pass

    return garde

#  Export PDF du planning
def exporter_planning_pdf(request, planning_id):
    planning = get_object_or_404(PlanningWeekend, id=planning_id)
    
    # Génération du PDF depuis le template HTML
    buffer = BytesIO()
    html_string = render_to_string("planning_pdf.html", {"planning": planning, "logo_path": "static/images/logo.svg"})
    pisa_status = pisa.CreatePDF(src=html_string, dest=buffer)
    buffer.seek(0)

    if pisa_status.err:
        return HttpResponse("Erreur génération PDF", status=500)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="planning_{planning.date_debut}_AstreintePro.pdf"'
    return response

#  Export Excel du planning
def exporter_planning_excel(planning):
    data = []
    for garde in planning.gardes.all():
        data.append({
            "Service": garde.service.nom_service,
            "Collaborateur": f"{garde.collaborateur.nom} {garde.collaborateur.prenom}",
            "Email": garde.collaborateur.email,
            "Téléphone": garde.collaborateur.telephone,
        })

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def generate_planning_pdf(planning):
    buffer = BytesIO()
    # On rend le template HTML avec le planning
    html_string = render_to_string("planning_pdf.html", {"planning": planning})
    pisa_status = pisa.CreatePDF(src=html_string, dest=buffer)
    buffer.seek(0)
    if pisa_status.err:
        raise Exception("Erreur génération PDF")
    return buffer

#  Envoi email avec planning complet
def envoyer_planning_complet(planning):
    # Utilise la fonction utilitaire qui retourne un BytesIO
    pdf_file = generate_planning_pdf(planning)
    excel_file = exporter_planning_excel(planning)

    destinataires = list(Collaborateur.objects.values_list("email", flat=True)) + \
                    list(ChefService.objects.values_list("email", flat=True))

    sujet = f"Planning du {planning.date_debut} au {planning.date_fin}"
    message = (
        f"Bonjour,\n\n"
        f"Veuillez trouver ci-joint le planning des astreintes pour le weekend du "
        f"{planning.date_debut} au {planning.date_fin}.\n\n"
        "Merci de votre collaboration.\n\n"
        "-- Équipe AstreintePro"
    )

    email = EmailMessage(sujet, message, settings.EMAIL_HOST_USER, destinataires)
    pdf_file.seek(0)
    email.attach(f"planning_{planning.date_debut}.pdf", pdf_file.read(), "application/pdf")
    excel_file.seek(0)
    email.attach(f"planning_{planning.date_debut}.xlsx", excel_file.read(), "application/vnd.ms-excel")

    try:
        email.send()
    except Exception as e:
        print("Erreur envoi email:", e)

#  Vue pour afficher planning (auto-généré le lundi)
def planning_weekend(request):
    today = date.today()
    prochain_samedi = today + timedelta((5 - today.weekday()) % 7)
    dimanche = prochain_samedi + timedelta(days=1)

    # Chaque lundi → régénération forcée
    if today.weekday() == 0:
        planning = generer_planning_weekend(start_date=today, force=True)
    else:
        # On prend le premier planning existant
        planning = PlanningWeekend.objects.filter(
            date_debut=prochain_samedi,
            date_fin=dimanche
        ).first()

        # S’il n’existe pas → on le génère
        if not planning:
            planning = generer_planning_weekend(start_date=today, force=True)


    return render(request, "planning_weekend.html", {"planning": planning})


       #  Régénérer automatiquement si une indispo est acceptée
def changer_statut_indisponibilite(request, id_indisponibilite, action):
    indispo = get_object_or_404(Indisponibilite, pk=id_indisponibilite)

    if action == "accepter":
        indispo.statut = "acceptee"
    elif action == "refuser":
        indispo.statut = "refusee"
    indispo.save()

    if indispo.statut == "acceptee":
        plannings = PlanningWeekend.objects.filter(
            date_debut__lte=indispo.date_fin,
            date_fin__gte=indispo.date_debut
        )
        for planning in plannings:
            service = indispo.collaborateur.service

            # 🔹 Chercher un remplaçant disponible
            candidats = Collaborateur.objects.filter(service=service).exclude(
                indisponibilite__statut="acceptee",
                indisponibilite__date_debut__lte=planning.date_fin,
                indisponibilite__date_fin__gte=planning.date_debut
            ).exclude(
                pk=indispo.collaborateur.pk
            ).order_by("nombre_gardes", "matricule")

            if candidats.exists():
                nouveau = candidats.first()

                # Supprimer l'ancien collaborateur seulement si un remplaçant existe
                Garde.objects.filter(planning=planning, collaborateur=indispo.collaborateur).delete()

                # Créer la nouvelle garde
                Garde.objects.create(planning=planning, service=service, collaborateur=nouveau)
                nouveau.nombre_gardes = (nouveau.nombre_gardes or 0) + 1
                nouveau.save()
            else:
                # 🔹 Aucun remplaçant disponible → on garde la garde actuelle et on notifie éventuellement
                pass

    return redirect("list_indisponibilites")

def list_indisponibilites(request):
    if 'admin_id' not in request.session and 'secretaire_id' not in request.session:
        return redirect('home')

    indispo = Indisponibilite.objects.all()
    # anciennement render via redirect avec context — on redirige simplement vers la gestion
    if request.session.get('admin_id'):
        return redirect("/gestion_utilisateurs/?tab=indisponibilites")
    elif request.session.get('secretaire_id'):
        return redirect("/gestion_utilisateurs_secretaire/?tab=indisponibilites")
    else:
        return redirect('home')

def strategie(request):
    return render(request, "strategie.html")

def a_propos(request):
    return render(request, "a_propos.html")

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        role = request.GET.get("role", "admin")  

        # Vérifier si un utilisateur existe avec cet email
        user = None
        if role == "admin":
            user = Admin.objects.filter(email=email).first()
        elif role == "secretaire":
            user = Secretaire.objects.filter(email=email).first()
        elif role == "chef":
            user = ChefService.objects.filter(email=email).first()

        if user:
            code = str(random.randint(100000, 999999))  # 6 chiffres
            PasswordResetCode.objects.create(user_email=email, code=code, role=role)

            try:
                send_mail(
                    "Code de réinitialisation",
                    f"Bonjour,\n\nVoici votre code : {code}\nValable 15 minutes.",
                    settings.EMAIL_HOST_USER,
                    [email],
                )
                messages.success(request, "✅ Code envoyé par email.")
                return redirect("password_reset_verify")  
            except Exception as e:
                print("Erreur envoi email:", e)
                messages.error(request, "Erreur lors de l'envoi d'email.")
        else:
            messages.error(request, "❌ Aucun compte trouvé avec cet email.")


    return render(request, "password_reset_request.html") 

def password_reset_verify(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")
        new_password = request.POST.get("password")

        reset_code = PasswordResetCode.objects.filter(user_email=email, code=code).last()
        if reset_code and reset_code.is_valid():
            # Trouver le user
            user = Admin.objects.filter(email=email).first() or \
                   Secretaire.objects.filter(email=email).first() or \
                   ChefService.objects.filter(email=email).first()

            if user:
                user.password = make_password(new_password)
                user.save()
                messages.success(request, "✅ Mot de passe réinitialisé.")
                return redirect("login_admin")
        else:
            messages.error(request, "❌ Code invalide ou expiré.")

    return render(request, "password_reset_verify.html")
