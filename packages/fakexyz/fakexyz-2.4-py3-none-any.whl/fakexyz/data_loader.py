import os
import json

def _validate_data_structure(data, filename, warnings_list):
    """
    Validates the structure of the loaded JSON data for a given country.
    Checks for the presence of expected keys in address entries.
    Appends warnings to the provided warnings_list.
    """
    
    expected_address_keys = [
        "Street", "City/Town", "State/Province/Region", "Zip/Postal Code",
        "Phone Number", "Country", "Latitude", "Longitude", "Full Name",
        "Gender", "Birthday", "Social Security Number", "Credit card brand",
        "Credit card number", "Expire", "CVV", "Country_Code"
    ]

    if not isinstance(data, list):
        warnings_list.append(f"Warning: '{filename}' root is not a list of addresses.")
        return
    
    for i, address in enumerate(data):
        for key in expected_address_keys:
            if key not in address:
                warnings_list.append(f"Warning: '{filename}' address entry {i} is missing key: '{key}'")


def load_data():
    data = {}
    warnings_list = []
    country_name_map = {}
    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(current_dir, "data")
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            country_code = filename.split(".")[0]
            file_path = os.path.join(data_dir, filename)
            with open(file_path, encoding="utf-8") as f:
                country_addresses = json.load(f)
                
                # Assuming all addresses in a file belong to the same country
                # and the first address contains the country name and code.
                if country_addresses and isinstance(country_addresses, list) and len(country_addresses) > 0:
                    first_address = country_addresses[0]
                    full_country_name = first_address.get("Country", "").lower()
                    
                    # Store the list of addresses directly under the country code
                    data[country_code] = {
                        "meta": {
                            "country": first_address.get("Country", ""),
                            "country_code": first_address.get("Country_Code", "").upper(),
                            "country_flag": "", # No flag in new data, keep empty
                            "currency": "" # No currency in new data, keep empty
                        },
                        "addresses": country_addresses
                    }
                    
                    _validate_data_structure(country_addresses, filename, warnings_list) # Validate the list of addresses
                    
                    if full_country_name:
                        country_name_map[full_country_name] = country_code
                else:
                    warnings_list.append(f"Warning: '{filename}' is empty or not a list of addresses.")
    return data, warnings_list, country_name_map
