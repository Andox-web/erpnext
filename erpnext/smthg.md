Guide d'Implémentation d'un Calendrier dans Frappe/ERPNext
(Avec personnalisation des affichages et fonctions avancées)

1. Afficher des Événements
a. Structure de base :
Les événements sont chargés depuis un DocType (ex: "Calendar Event") via une méthode API.

javascript
const calendar = new frappe.views.Calendar({
    parent: $(calendarEl),              // Élément HTML conteneur
    doctype: 'Calendar Event',           // DocType source
    field_map: {                         // Mapping des champs
        start: 'start_date',             // Champ datetime de début
        end: 'end_date',                 // Champ datetime de fin  
        id: 'name',                      // Identifiant unique
        title: 'title',                  // Titre de l'événement
        color: 'event_color'             // Champ optionnel pour la couleur
    },
    initial_view: 'dayGridMonth'         // Vue par défaut (dayGridWeek, timeGridDay)
});
b. Personnaliser l'affichage :

Couleurs conditionnelles :

javascript
field_map: {
    ...,
    color: (event) => event.status === 'Urgent' ? '#ff0000' : '#00ff00'  
}  
Contenu HTML personnalisé :

javascript
eventDidMount: (info) => {
    info.el.innerHTML += `<div class="badge">${info.event.extendedProps.priority}</div>`;
}  
2. Ajouter des Interactions
a. Clic sur un événement :

javascript
calendar.setup_event_click = (event) => {
    // Ouvrir le document lié
    frappe.set_route('Form', 'Calendar Event', event.id);
    
    // Ou afficher un popup personnalisé
    frappe.msgprint(`Événement: ${event.title}`);
};  
b. Clic sur une date vide :

javascript
calendar.calendar.on('dateClick', (arg) => {
    frappe.prompt('Créer un événement', (value) => {
        frappe.db.insert('Calendar Event', {
            title: value,
            start_date: arg.dateStr
        }).then(() => calendar.refetch());
    });
});  
3. Intégrer des Fonctions Métier
a. Bouton personnalisé :

html
<!-- Dans le template HTML -->
<button class="btn btn-secondary" onclick="exportToGoogleCalendar()">
    Exporter vers Google
</button>  
javascript
function exportToGoogleCalendar() {
    frappe.call({
        method: 'my_app.api.export_to_google',
        args: { events: calendar.getVisibleEvents() },
        callback: (r) => console.log(r.message)
    });
}  
b. Synchronisation en arrière-plan :

python
# api.py
@frappe.whitelist()
def export_to_google(events):
    for event in json.loads(events):
        # Logique d'export vers Google Calendar
        frappe.enqueue(  
            method=google_api_export,  
            queue='long',  
            event=event  
        )  
    return {"status": "En cours..."}  
4. Personnalisations Avancées
a. Overlay de chargement :

javascript
calendar.refetch = () => {
    frappe.dom.freeze("Chargement...");
    calendar.fetch_events().finally(() => frappe.dom.unfreeze());
}  
b. Filtres dynamiques :

javascript
// Ajouter une dropdown de filtres
const filter = `<select id="event-filter">
    <option value="all">Tous</option>
    <option value="meeting">Réunions</option>
</select>`;  

$('.calendar-header').prepend(filter);  

$('#event-filter').on('change', () => {
    calendar.update_options({
        filters: { event_type: $('#event-filter').val() }
    });
});  
5. Bonnes Pratiques
Performance :

Limiter les champs récupérés via fields dans get_events.

Utiliser frappe.db.get_list pour les grosses données.

Sécurité :

Toujours utiliser @frappe.whitelist pour les méthodes API.

Valider les permissions avec frappe.has_permission.

UX :

Ajouter un indicateur de chargement avec frappe.dom.freeze().

Gérer les erreurs avec frappe.msgprint(error.message).

Exemple Complet d'un Événement Dynamique :

javascript
// Créer un événement avec popup  
function createEventWithModal() {
    const dialog = new frappe.ui.Dialog({
        title: 'Nouvel Événement',
        fields: [
            {'label': 'Titre', 'fieldname': 'title', 'fieldtype': 'Data'},
            {'label': 'Date', 'fieldname': 'date', 'fieldtype': 'Date'}
        ],
        primary_action: (values) => {
            frappe.db.insert('Calendar Event', {
                title: values.title,
                start_date: values.date
            }).then(() => {
                dialog.hide();
                calendar.refetch();
            });
        }
    });
    dialog.show();
}  
📌 Tips Pro :

Utilisez console.log(calendar.getView()) pour déboguer la vue actuelle.

Explorez FullCalendar Docs pour plus d'options.

Stockez les préférences utilisateur avec frappe.ui.set_user_settings().

Ce système peut être étendu pour gérer des :

🎯 Rappels automatiques par email

🤖 Intégrations Zoom/Teams

📊 Tableaux de bord de disponibilité

🔄 Synchronisation bi-directionnelle