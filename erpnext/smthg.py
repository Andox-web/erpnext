"""
Frappe Framework - Guide des Fonctionnalités Clés

Ce fichier démontre les fonctionnalités les plus utilisées :
- Gestion de fichiers
- Opérations DB (avec relations)
- Emails & notifications
- Fonctions courantes
"""

import frappe
from frappe import _
from frappe.utils import get_url, nowdate, add_days
import os

# ---------------------------
# 1. GESTION DE FICHIERS
# ---------------------------

def handle_files():
    # Création fichier
    with open('sample.txt', 'w') as f:
        f.write('Contenu exemple')

    # Lecture fichier
    with open('sample.txt', 'r') as f:
        content = f.read()
        print(content)

    # Upload fichier depuis l'UI
    def upload_file(file_path, doctype, docname):
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        file_doc = frappe.get_doc({
            'doctype': 'File',
            'file_name': os.path.basename(file_path),
            'attached_to_doctype': doctype,
            'attached_to_name': docname,
            'content': file_content
        })
        file_doc.insert()
        return file_doc

    # Download fichier
    def download_file(file_url):
        file_path = frappe.get_site_path() + '/' + file_url
        with open(file_path, 'rb') as f:
            file_data = f.read()
        return file_data

# ---------------------------
# 2. OPERATIONS DATABASE
# ---------------------------

def db_operations():
    # Création document
    new_user = frappe.get_doc({
        'doctype': 'User',
        'email': 'user@example.com',
        'first_name': 'Jean',
        'roles': [{'role': 'System Manager'}]
    })
    new_user.insert()

    # Requête simple
    users = frappe.get_all('User', 
        filters={'enabled': 1},
        fields=['first_name', 'email']
    )

    # Requête avec jointure
    orders = frappe.db.sql("""
        SELECT 
            cust.customer_name, 
            ord.transaction_date, 
            ord.grand_total
        FROM 
            `tabSales Order` ord
        LEFT JOIN 
            `tabCustomer` cust
        ON 
            ord.customer = cust.name
        WHERE 
            ord.status = 'Open'
    """, as_dict=True)

    # Update document
    frappe.db.set_value('User', 'user@example.com', 'last_name', 'Dupont')

    # Transaction DB
    try:
        frappe.db.commit()
    except:
        frappe.db.rollback()
        raise

# ---------------------------
# 3. EMAILS & NOTIFICATIONS
# ---------------------------

def send_communication():
    # Email simple
    frappe.sendmail(
        recipients=['user@example.com'],
        subject='Nouvelle notification',
        message='Contenu du message',
        reference_doctype='User',
        reference_name='user@example.com'
    )

    # Notification système
    frappe.publish_realtime(
        event='msgprint',
        message='Action terminée!',
        user=frappe.session.user
    )

    # Notification log
    frappe.get_doc({
        'doctype': 'Notification Log',
        'subject': 'Nouvel événement',
        'for_user': 'user@example.com',
        'type': 'Alert'
    }).insert()

# ---------------------------
# 4. FONCTIONS COURANTES
# ---------------------------

def common_utilities():
    # Gestion des erreurs
    try:
        # code
        pass
    except Exception as e:
        frappe.throw(_('Erreur: {0}').format(str(e)))

    # Permissions
    if not frappe.has_permission('User', 'read'):
        frappe.throw(_('Permission refusée'))

    # Cache
    cache_key = 'my_data'
    frappe.cache().set_value(cache_key, {'data': 'value'})
    cached_data = frappe.cache().get_value(cache_key)

    # Background job
    frappe.enqueue(
        method='frappe.utils.background_jobs.execute_job',
        job_name='my_background_task',
        docs=[],
        timeout=300
    )

    # Logs
    frappe.log_error('Message d\'erreur', 'Erreur Custom')

    # Dates
    today = nowdate()
    next_week = add_days(today, 7)

# ---------------------------
# 5. SECURITE & BEST PRACTICES
# ---------------------------

def security_checks():
    # Validation avant sauvegarde
    def validate(doc, method):
        if doc.value < 0:
            frappe.throw(_("Valeur ne peut pas être négative"))

    # Protection CSRF
    @frappe.whitelist()
    def secure_method():
        pass

    # Whitelisting des méthodes
    @frappe.whitelist()
    def api_endpoint():
        return {'status': 'success'}

# ---------------------------
# 6. INTERACTION AVEC JSON
# ---------------------------

def json_operations():
    # Écrire un fichier JSON
    data = {
        "user": "john@doe.com",
        "roles": ["System Manager", "Support"],
        "meta": {"created": "2024-01-01"}
    }
    
    with open('user_data.json', 'w') as f:
        import json
        json.dump(data, f, indent=2)

    # Lire un fichier JSON
    with open('user_data.json', 'r') as f:
        loaded_data = json.load(f)
        print(f"Données JSON: {loaded_data}")

    # Enregistrer en tant que document File dans Frappe
    def save_json_as_file():
        file_doc = frappe.get_doc({
            'doctype': 'File',
            'file_name': 'user_config.json',
            'attached_to_doctype': 'User',
            'attached_to_name': 'john@doe.com',
            'content': json.dumps(data, indent=2)
        })
        file_doc.insert()
        return file_doc

# ---------------------------
# 7. INTERACTION AVEC CSV
# ---------------------------

def csv_operations():
    # Écrire un fichier CSV
    import csv
    headers = ['Nom', 'Email', 'Role']
    users = [
        ['Jean Dupont', 'jean@example.com', 'Manager'],
        ['Marie Curie', 'marie@example.com', 'Scientist']
    ]
    
    with open('users.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(users)

    # Lire un fichier CSV
    with open('users.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"Ligne CSV: {row}")

    # Utiliser pandas pour les CSV complexes (nécessite pandas)
    def pandas_csv_operations():
        import pandas as pd
        
        # Lire avec pandas
        df = pd.read_csv('users.csv')
        print(f"DataFrame:\n{df.head()}")
        
        # Filtrer et exporter
        filtered = df[df['Role'] == 'Manager']
        filtered.to_csv('managers.csv', index=False)

    # Exporter des données depuis la base de données vers CSV
    def export_to_csv():
        users = frappe.get_all('User',
            fields=['name', 'first_name', 'email', 'enabled'],
            filters={'enabled': 1}
        )
        
        with open('users_export.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Prénom', 'Email', 'Actif'])
            
            for user in users:
                writer.writerow([
                    user.name,
                    user.first_name,
                    user.email,
                    'Oui' if user.enabled else 'Non'
                ])

# ---------------------------
# 8. INTERACTION AVEC LES APIs
# ---------------------------

def api_operations():
    # ---------------------------
    # Client API - Appeler des APIs externes
    # ---------------------------
    
    import requests
    from frappe.utils import get_request_session
    
    # GET simple
    def call_get_api():
        response = requests.get(
            'https://api.example.com/data',
            headers={'Authorization': 'Bearer YOUR_TOKEN'},
            params={'page': 1, 'limit': 100}
        )
        response.raise_for_status()
        return response.json()

    # POST avec données JSON
    def call_post_api():
        payload = {
            'doctype': 'User',
            'email': 'api@user.com',
            'first_name': 'API User'
        }
        
        with get_request_session() as session:
            response = session.post(
                'https://api.example.com/create',
                json=payload,
                timeout=10
            )
            
        if response.status_code == 201:
            return response.json()['data']
        else:
            frappe.throw(f"Erreur API: {response.text}")

    # Gestion avancée avec retry
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    def call_api_with_retry():
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504]
        )
        session.mount('https://', HTTPAdapter(max_retries=retries))
        
        try:
            return session.get('https://api.example.com/unstable-endpoint')
        except requests.exceptions.RetryError:
            frappe.log_error("Échec après 3 tentatives API")

    # ---------------------------
    # Server API - Exposer des endpoints
    # ---------------------------
    
    # API simple GET
    @frappe.whitelist(allow_guest=True)
    def get_public_data():
        return {
            'status': 'success',
            'data': frappe.get_all('User', fields=['name', 'email'])
        }

    # API POST avec validation
    @frappe.whitelist()
    def create_user(**kwargs):
        # Validation des paramètres
        if not kwargs.get('email'):
            frappe.throw("Email obligatoire")
            
        user = frappe.get_doc({
            'doctype': 'User',
            'email': kwargs['email'],
            'first_name': kwargs.get('first_name', ''),
            'roles': [{'role': kwargs.get('role', 'Customer')}]
        }).insert()
        
        return {
            'status': 'created',
            'user_id': user.name
        }

    # API RESTful avec routes
    # Ajouter dans hooks.py:
    """
    hooks = {
        'api_routes': [
            {'route': '/api/v1/users', 'handler': 'my_app.api.get_users'},
            {'route': '/api/v1/users/<id>', 'handler': 'my_app.api.get_user'}
        ]
    }
    """

# ---------------------------
# 9. SECURITE API
# ---------------------------

def api_security():
    # Authentification JWT
    from frappe.utils.jwt import JWT
    
    def generate_api_token(user):
        jwt = JWT()
        return jwt.encode({
            'user': user,
            'exp': frappe.utils.add_to_date(None, days=1)
        })

    # Validation de token
    @frappe.whitelist()
    def protected_endpoint():
        token = frappe.request.headers.get('Authorization', '').split(' ')[-1]
        try:
            data = JWT().decode(token)
            frappe.set_user(data['user'])
            # Logique métier
        except Exception as e:
            frappe.throw("Token invalide", exc=e)

    # Limite de taux
    from frappe.rate_limiter import rate_limit
    
    @rate_limit(key='user', limit=10, seconds=60)
    @frappe.whitelist()
    def limited_api():
        return "Vous pouvez appeler cette API 10 fois par minute"

