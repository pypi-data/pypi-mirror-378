import requests
from datetime import datetime

class NordiciteAPIClient:               
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("❌ Une clé API est requise pour initialiser le client Nordicité.")
        
        self.api_key = api_key
        self.base_url = "https://public.api.nordicite.io"
        self.headers = {
            "accept": "*/*",
            "api-key": self.api_key
        }

    def _make_request(self, endpoint, params):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur requête vers {url} : {e}")
            return None

    def get_data_source(self, organizationId=None, name=None, include=None, disabled=None):
        params = {
            "organizationId": organizationId,
            "name": name,
            "include": include
        }
        return self._make_request("/data-source", params)
    
    def get_organization(self, slug=None, disabled=None):
        params = {
            "slug": slug,
            "disabled": disabled
        }
        return self._make_request("/organization", params)
    
    def get_equipment_attribute(self, organizationId, equipmentId, attributeId, disabled=None, include=None):
        params = {
            "organizationId":organizationId,
            "equipmentId":equipmentId,
            "attributeId":attributeId,
            "disabled":disabled,
            "include":include,   
        }
        return self._make_request("/equipment-attribute", params)
        

    def get_equipment_entry(self, equipment_id, entry_type, interval, start_date, end_date, page=0):
        params = {
            "equipmentId": equipment_id,
            "type": entry_type,
            "interval": interval,
            "startDate": start_date,
            "endDate": end_date,
            "page": page
        }
        return self._make_request("/equipment-entry", params)


    def get_equipment_entry_multi_page(self, equipment_id, entry_type, interval, start_date, end_date):
        results = []
        page = 0
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")

        try:
            while True:
                data = self.get_equipment_entry(
                    equipment_id=equipment_id,
                    entry_type=entry_type,
                    interval=interval,
                    start_date=start_date,
                    end_date=end_date,
                    page=page
                )

                if not data or "values" not in data or not data["values"]:
                    print("Plus de données à récupérer.")
                    break

                results.extend(data["values"])

                latest_timestamp = data["values"][-1]["timestamp"]
                latest_timestamp_dt = datetime.strptime(latest_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

                if latest_timestamp_dt >= end_date_dt:
                    break
                print(f"page :{page}")
                page += 1

            return {"values":results}
        except Exception as e:
            return {"error": str(e)}
        
    def filter_equipment_entry(self, values, expected, key="equipmentAttributeId"):
        """
        Filtre les entrées d'équipements selon une clé/valeur dans metadata.

        Args:
            values (list): Liste de dictionnaires retournés par l'API (/equipment-entry).
            key (str): Clé dans metadata (par défaut "equipmentAttributeId").
            expected: Valeur attendue dans metadata[key].

        Returns:
            list: Liste filtrée des valeurs correspondant au critère.
        """
        if not values:
            return []

        return [
            entry for entry in values
            if entry.get("metadata", {}).get(key) == expected
        ]


# Exemple d'utilisation
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()
    api_key = os.getenv("API_KEY")
    client = NordiciteAPIClient(api_key)

    # Test d'appel à l'endpoint /organization
    #org_data = client.get_organization(slug=None, disabled=None)
    #print("\nOrganization:", org_data)   

    # Test d'appel à l'endpoint /data-source
    #ds_data = client.get_data_source(organizationId=None, name="Station de traitement", include = 'equipments', disabled = None)
    #print("\nData source:", ds_data)
    
    #ea_data = client.get_equipment_attribute(
    #    organizationId = None, 
    #    equipmentId = 1486,
    #    attributeId = None,
    #    disabled=None, 
    #    include=None        
    #)
    #print("\nEquipment Attribute:", ea_data)

    # Test d'appel à l'endpoint /equipment-entry
    #ee_data = client.get_equipment_entry(
    #    equipment_id=1486,
    #    entry_type="sensor",
    #    interval=1,
    #    start_date="2024-01-01T00:00:00.000Z",
    #    end_date="2024-01-02T00:00:00.000Z"
    #)

    #print("\nEquipment entry:", ee_data)

    # Test d'appel à l'endpoint /equipment-entry multi page
    ee_multi_page_data = client.get_equipment_entry_multi_page(
        equipment_id=1486,
        entry_type="sensor",
        interval=1,
        start_date="2024-01-01T00:00:00.000Z",
        end_date="2024-01-01T02:00:00.000Z"
    )
    #print("\nEquipment entry multi page:",  ee_multi_page_data)
    

    ee_multi_page_data_filtered = client.filter_equipment_entry(values = ee_multi_page_data['values'] , 
                                                    expected = 5447, 
                                                    key = "equipmentAttributeId")
    print(f"\nEquipment entry multi page filtré par equipmentAttributeId : {ee_multi_page_data_filtered}")
    

    
    


