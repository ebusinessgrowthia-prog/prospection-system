# Google Sheets Schema Configuration
GOOGLE_SHEETS_SCHEMA = {
    "Prospects": {
        "columns": [
            "id",
            "nom_complet",
            "email",
            "entreprise",
            "secteur",
            "url_site",
            "source",
            "date_decouverte",
            "score_validation",
            "statut_validation",
            "statut_prospection",
            "date_dernier_contact",
            "nombre_contacts",
            "dernier_message_envoye",
            "reponse_recue",
            "tags",
            "notes"
        ],
        "column_headers": [
            "ID",
            "Nom Complet",
            "Email",
            "Entreprise",
            "Secteur",
            "URL Site",
            "Source",
            "Date Découverte",
            "Score Validation",
            "Statut Validation",
            "Statut Prospection",
            "Date Dernier Contact",
            "Nombre Contacts",
            "Dernier Message Envoyé",
            "Réponse Reçue",
            "Tags",
            "Notes"
        ]
    },
    "Emails": {
        "columns": [
            "id",
            "prospect_id",
            "objet",
            "corps",
            "date_envoi",
            "statut",
            "ouvert",
            "clic",
            "reponse",
            "bounce",
            "variant",
            "score_personnalisation"
        ],
        "column_headers": [
            "ID",
            "Prospect ID",
            "Objet",
            "Corps",
            "Date Envoi",
            "Statut",
            "Ouvert",
            "Clic",
            "Réponse",
            "Bounce",
            "Variant",
            "Score Personnalisation"
        ]
    },
    "Performance": {
        "columns": [
            "date",
            "campagnes_envoyees",
            "emails_envoyes",
            "taux_ouverture",
            "taux_clic",
            "taux_reponse",
            "taux_bounce",
            "nouveaux_prospects",
            "prospects_valides"
        ],
        "column_headers": [
            "Date",
            "Campagnes Envoyées",
            "Emails Envoyés",
            "Taux Ouverture (%)",
            "Taux Clic (%)",
            "Taux Réponse (%)",
            "Taux Bounce (%)",
            "Nouveaux Prospects",
            "Prospects Validés"
        ]
    },
    "Optimisation": {
        "columns": [
            "date",
            "dork",
            "efficacite",
            "prospects_trouves",
            "emails_valides",
            "taux_conversion",
            "recommandation"
        ],
        "column_headers": [
            "Date",
            "Google Dork",
            "Efficacité",
            "Prospects Trouvés",
            "Emails Validés",
            "Taux Conversion (%)",
            "Recommandation"
        ]
    }
}

# Validation status options
VALIDATION_STATUS = {
    "VALID": "Valide",
    "INVALID": "Invalide",
    "PENDING": "En attente",
    "ERROR": "Erreur"
}

# Prospection status options
PROSPECTION_STATUS = {
    "NEW": "Nouveau",
    "CONTACTED": "Contacté",
    "RESPONDED": "A répondu",
    "INTERESTED": "Intéressé",
    "NOT_INTERESTED": "Pas intéressé",
    "BOUNCED": "Bounce",
    "UNSUBSCRIBED": "Désinscrit"
}