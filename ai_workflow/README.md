# AI Workflow - Industrialiser un Workflow AI depuis Notion

Ce module permet d'industrialiser l'exécution de workflows AI en intégrant Notion comme système de gestion de workflows et en exécutant des prompts AI de manière automatisée pour des applications SaaS.

## Vue d'ensemble

Le système se compose de trois composants principaux :

1. **Notion Client** - Récupère les configurations de workflows depuis une base de données Notion
2. **AI Executor** - Exécute les prompts AI via l'API OpenAI ou compatible
3. **Workflow Orchestrator** - Coordonne l'exécution et met à jour les statuts dans Notion

## Architecture

```
┌─────────────┐
│   Notion    │  ← Définition des workflows
│  Database   │     (Prompts, configurations)
└──────┬──────┘
       │
       ↓
┌─────────────────────┐
│     Orchestrator    │  ← Coordination
│  (orchestrator.py)  │
└─────────┬───────────┘
          │
          ├──→ ┌──────────────┐
          │    │ Notion Client│  ← Lecture/Écriture Notion
          │    └──────────────┘
          │
          └──→ ┌──────────────┐
               │ AI Executor  │  ← Exécution des prompts
               └──────────────┘
```

## Installation

### Prérequis

- Python 3.8+
- Compte Notion avec API key
- Compte OpenAI avec API key

### Dépendances

Ajoutez les dépendances suivantes au `requirements.txt` :

```txt
notion-client>=2.0.0
openai>=1.0.0
python-dotenv>=1.0.0
```

Installation :

```bash
pip install -r requirements.txt
```

## Configuration

### 1. Configuration Notion

Créez une base de données Notion avec les propriétés suivantes :

| Propriété       | Type         | Description                                    |
|----------------|--------------|------------------------------------------------|
| Name           | Title        | Nom du workflow                                |
| Status         | Select       | Statut (Active, Running, Completed, Failed)    |
| Prompt         | Text         | Le prompt à exécuter                           |
| System Message | Text         | Message système optionnel                      |
| Temperature    | Number       | Température (0-2), défaut: 0.7                 |
| Max Tokens     | Number       | Nombre max de tokens (optionnel)               |
| Result         | Text         | Résultat de l'exécution (mis à jour auto)      |
| Last Executed  | Date         | Date de dernière exécution (mis à jour auto)   |

Options pour le champ **Status** :
- `Active` - Workflows prêts à être exécutés
- `Running` - En cours d'exécution
- `Completed` - Exécution réussie
- `Failed` - Échec de l'exécution

### 2. Obtenir les API Keys

**Notion API Key:**
1. Allez sur https://www.notion.so/my-integrations
2. Créez une nouvelle intégration
3. Copiez le "Internal Integration Token"
4. Partagez votre base de données avec l'intégration

**Notion Database ID:**
- URL de votre base de données : `https://notion.so/[workspace]/[DATABASE_ID]?v=...`
- Copiez la partie `DATABASE_ID` (32 caractères)

**OpenAI API Key:**
1. Allez sur https://platform.openai.com/api-keys
2. Créez une nouvelle API key
3. Copiez la clé

### 3. Configuration du module

Copiez le fichier de configuration exemple :

```bash
cd ai_workflow/config
cp config.env.example config.env
```

Éditez `config.env` avec vos clés :

```env
NOTION_API_KEY=secret_xxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AI_MODEL=gpt-3.5-turbo
WORKFLOW_STATUS_FILTER=Active
MAX_WORKFLOWS_PER_RUN=10
DRY_RUN=false
LOG_LEVEL=INFO
```

## Utilisation

### Test de la connexion AI

```bash
cd ai_workflow
python examples/test_ai_executor.py
```

### Test de l'intégration Notion

```bash
cd ai_workflow
python examples/test_notion_client.py
```

### Exécution des workflows

```bash
cd ai_workflow
python examples/run_workflows.py
```

### Utilisation programmatique

```python
from ai_workflow.src.orchestrator import WorkflowOrchestrator

# Initialiser l'orchestrateur
orchestrator = WorkflowOrchestrator(
    notion_api_key="your_notion_key",
    openai_api_key="your_openai_key",
    ai_model="gpt-3.5-turbo"
)

# Valider la configuration
validation = orchestrator.validate_setup()
print(f"Setup valid: {validation['overall']}")

# Exécuter les workflows depuis Notion
results = orchestrator.run_workflows_from_database(
    database_id="your_database_id",
    status_filter="Active",
    dry_run=False,
    max_workflows=10
)

# Afficher les résultats
for result in results:
    print(f"Workflow: {result['workflow_name']}")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Response: {result['response']}")
```

## Intégration avec GitHub Actions

Créez un workflow GitHub Actions pour exécuter automatiquement vos workflows AI :

```yaml
name: Run AI Workflows

on:
  schedule:
    - cron: '0 * * * *'  # Chaque heure
  workflow_dispatch:      # Déclenchement manuel

jobs:
  run-workflows:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run AI Workflows
        env:
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}
          NOTION_DATABASE_ID: ${{ secrets.NOTION_DATABASE_ID }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          cd ai_workflow
          python examples/run_workflows.py
```

N'oubliez pas d'ajouter vos secrets dans GitHub :
- Settings → Secrets and variables → Actions → New repository secret

## Structure du projet

```
ai_workflow/
├── config/
│   ├── config.py              # Gestionnaire de configuration
│   └── config.env.example     # Exemple de configuration
├── src/
│   ├── __init__.py
│   ├── notion_client.py       # Client Notion
│   ├── ai_executor.py         # Exécuteur AI
│   └── orchestrator.py        # Orchestrateur
├── examples/
│   ├── run_workflows.py       # Script principal
│   ├── test_ai_executor.py    # Test AI
│   └── test_notion_client.py  # Test Notion
└── README.md
```

## Cas d'usage

### 1. Génération de contenu automatisée

Créez des workflows dans Notion pour générer automatiquement du contenu :
- Articles de blog
- Descriptions de produits
- Emails marketing
- Documentation technique

### 2. Analyse de données

Utilisez l'AI pour analyser des données et générer des insights :
- Résumés de rapports
- Analyse de sentiment
- Extraction d'informations clés
- Recommandations

### 3. Automatisation de tâches

Automatisez des tâches répétitives :
- Réponses aux questions fréquentes
- Classification de tickets
- Traduction de contenu
- Génération de code

### 4. Workflows personnalisés SaaS

Intégrez dans votre application SaaS :
- Workflows clients personnalisés
- Traitement de requêtes utilisateur
- Génération de rapports personnalisés
- Assistant virtuel intelligent

## Sécurité

⚠️ **Important** :

- Ne commitez jamais vos clés API dans Git
- Utilisez des variables d'environnement ou des secrets
- Le fichier `config.env` doit être dans `.gitignore`
- Limitez les permissions de vos API keys
- Surveillez l'utilisation de vos APIs

## Monitoring et Logs

Les logs incluent :
- Démarrage/fin de chaque workflow
- Résultats d'exécution
- Erreurs détaillées
- Utilisation des tokens

Configuration du niveau de log dans `config.env` :
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## Gestion des erreurs

Le système gère automatiquement :
- Échecs de connexion API
- Timeouts
- Erreurs de parsing
- Mise à jour du statut "Failed" dans Notion
- Logs détaillés des erreurs

## Limites et considérations

- **Rate limits** : Respectez les limites des APIs (Notion et OpenAI)
- **Coûts** : L'utilisation d'OpenAI API est facturée par token
- **Timeouts** : Les prompts très longs peuvent timeout
- **Taille des réponses** : Notion limite la taille des textes (2000 caractères)

## Support et contribution

Pour toute question ou amélioration, ouvrez une issue sur GitHub.

## Licence

Ce projet suit la licence du repository principal.
