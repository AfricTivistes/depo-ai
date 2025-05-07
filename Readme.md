# API d'Analyse d'Audit de Sécurité

API Flask permettant d'analyser automatiquement les réponses à un audit de sécurité et de générer des recommandations via l'intelligence artificielle.

## Présentation

Cette API utilise l'intelligence artificielle pour analyser les réponses fournies lors d'un audit de sécurité informatique. Elle identifie automatiquement le type d'audit, évalue le niveau de sécurité global, détecte les points forts et les vulnérabilités, puis génère des recommandations personnalisées.

## Fonctionnalités

- **Détection automatique du type d'audit** (complet ou spécifique à un domaine)
- **Analyse des réponses** par IA spécialisée en cybersécurité
- **Évaluation du niveau de sécurité** avec score sur 10
- **Identification des points forts** et leur importance
- **Détection des vulnérabilités** et classification par niveau de risque
- **Génération de recommandations détaillées** pour remédier aux failles
- **Production d'un résumé** de la situation et des étapes prioritaires

## Prérequis

- Python 3.7+
- Bibliothèques: Flask, Requests
- Clé API OpenRouter (ou autre fournisseur de modèles LLM)

## Installation

1. Clonez le dépôt:
```bash
git clone https://github.com/AfricTivistes/adisa.git
cd adisa
```

2. Installez les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurez votre clé API dans `app.py` ou via une variable d'environnement.

## Utilisation

### Démarrer l'API

```bash
python app.py
```

L'API sera accessible par défaut sur `http://localhost:5000`.

### Endpoints

#### 1. Analyse d'audit

**Endpoint**: `POST /api/analyze`

**Description**: Analyse les réponses d'un audit de sécurité et génère une évaluation complète.

**Format de requête**:
```json
{
  "Question 1": "Réponse 1",
  "Question 2": "Réponse 2",
  "Comment gérez-vous les mots de passe?": "Nous utilisons un gestionnaire de mots de passe d'entreprise",
  ...
}
```

**Format de réponse**:
```json
{
  "status": "success",
  "audit_type": "Audit spécifique: Politique de mots de passe",
  "evaluation": {
    "score": 7,
    "level": "Bon"
  },
  "strengths": [
    {
      "text": "Utilisation d'un gestionnaire de mots de passe centralisé",
      "rating": "Fort"
    },
    ...
  ],
  "weaknesses": [
    {
      "text": "Absence de politique de changement régulier des mots de passe",
      "rating": "Moyen"
    },
    ...
  ],
  "recommendations": [
    "Mettre en place une authentification à deux facteurs pour tous les services critiques",
    "Automatiser la détection des mots de passe faibles",
    ...
  ],
  "summary": "La gestion des mots de passe présente un bon niveau général mais nécessite des améliorations..."
}
```

#### 2. Vérification de santé

**Endpoint**: `GET /api/health`

**Description**: Vérifie que l'API est opérationnelle.

**Format de réponse**:
```json
{
  "status": "ok",
  "message": "API d'analyse d'audit de sécurité opérationnelle"
}
```

## Personnalisation

### Modification du modèle d'IA

Vous pouvez modifier le modèle utilisé en changeant les paramètres dans le constructeur de la classe `SecurityAuditAnalyzer`:

```python
security_analyzer = SecurityAuditAnalyzer(
    api_key="votre-clé-api",
    model="autre-modèle"
)
```

### Types d'audits supportés

L'API détecte automatiquement plusieurs domaines de la cybersécurité:

- Politique de mots de passe
- Sécurité des réseaux
- Gestion des accès
- Protection des données
- Sécurité physique
- Formation et sensibilisation
- Gestion des incidents
- Conformité réglementaire

## Architecture du code

- `app.py` : Point d'entrée de l'application Flask et définition des routes
- `SecurityAuditAnalyzer` : Classe principale pour l'analyse des audits
  - `analyze_responses()` : Méthode principale d'analyse
  - `_build_prompt()` : Construction du prompt pour l'IA
  - `_detect_audit_type()` : Détection automatique du type d'audit
  - `_parse_analysis()` : Extraction des données structurées

## Sécurité

⚠️ **Attention**: Ne stockez jamais votre clé API directement dans le code en production. Utilisez plutôt des variables d'environnement ou un fichier de configuration sécurisé.

## Exemple d'utilisation avec cURL

```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "Avez-vous une politique de mots de passe?": "Oui, nous exigeons des mots de passe d'au moins 8 caractères",
    "Utilisez-vous l'authentification à deux facteurs?": "Seulement pour les comptes administrateurs",
    "À quelle fréquence les mots de passe sont-ils changés?": "Il n'y a pas d'obligation de changement"
  }'
```
