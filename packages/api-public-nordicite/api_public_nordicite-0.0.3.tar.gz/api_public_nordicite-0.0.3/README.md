# 📦 api-public-nordicite

Une librairie Python simple pour interagir avec l'API publique de Nordicité : extraction des organisations, sources de données, et mesures d'équipements.

## 🚀 Installation

### Option 1 — Depuis PyPI 

```bash
pip install api-public-nordicite
```

### Option 2 — En local 

```bash
git clone https://github.com/Nordikeau-Innovation/Library_Python_Api_Public_Nordicite.git
cd Library_Python_Api_Public_Nordicite
pip install -e .
```

## ⚙️ Configuration

Crée un fichier `.env` à la racine de ton projet contenant ta clé API :

```
API_KEY=ta_cle_api_nordicite_ici
```

---

## 🧩 Utilisation

```python
from nordicite_api.NordiciteAPIClient import NordiciteAPIClient
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()
api_key = os.getenv("API_KEY")

# Initialiser le client avec la clé API
client = NordiciteAPIClient(api_key=api_key)

# Appeler l'endpoint /organization
org_data = client.get_organization()
print("\nOrganization:", org_data)
```

---

## 📚 Fonctionnalités disponibles

| Méthode | Description |
|--------|-------------|
| `get_organization(slug=None, disabled=None)` | Récupère les organisations |
| `get_data_source(organizationId=None, name=None, include=None, disabled=None)` | Récupère les sources de données |
| `get_equipment_entry(equipment_id, entry_type, interval, start_date, end_date, page=0)` | Récupère les données d’un capteur |

---

## 🛠️ Dépendances

- `requests`
- `python-dotenv`

---

## 📄 Licence

MIT © Youssoupha Marega — Nordikeau Innovation
