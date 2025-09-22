import random
from .data_loader import load_data

# Load data and ignore warnings for this module
_data, _, _country_name_map = load_data()
_countries = list(_data.keys())

def _resolve_country_code(country_input):
    """
    Resolves a country input (code or name) to its official country code.
    Performs case-insensitive matching and suggests alternatives if not found.
    """
    if not country_input:
        return random.choice(_countries)

    country_input_lower = country_input.lower()

    # 1. Try direct country code match
    if country_input_lower in _countries:
        return country_input_lower
    
    # 2. Try full country name match
    if country_input_lower in _country_name_map:
        return _country_name_map[country_input_lower]

    # 3. Fuzzy matching for suggestions
    suggestion = None
    for code in _countries:
        full_name = _data[code]['meta']['country'].lower()
        if country_input_lower in full_name or full_name.startswith(country_input_lower):
            suggestion = f"{_data[code]['meta']['country']} (Code: {code.upper()})"
            break
    
    error_message = f"Country '{country_input}' not found."
    if suggestion:
        error_message += f" Did you mean {suggestion}?"
    raise ValueError(error_message)


def get_country_info(country_input=None):
    """
    Returns meta information for a specific country or a random country.
    """
    country_code = _resolve_country_code(country_input)
    return _data[country_code]["meta"]

def get_personal_profile(country_input=None):
    """
    Returns a random personal profile (name, gender, phone, avatar) for a specific country or a random country.
    """
    country_code = _resolve_country_code(country_input)
    country_data = _data[country_code]
    address = random.choice(country_data['addresses'])
    
    return {
        "name": address['Full Name'],
        "gender": address['Gender'],
        "phone_number": address['Phone Number'],
        "avatar_url": "", # No direct equivalent, keep empty
    }

def get_random_address(country_input=None):
    """
    Returns a random address for a specific country or a random country.
    """
    country_code = _resolve_country_code(country_input)
    country_data = _data[country_code]
    address = random.choice(country_data['addresses'])
    
    return {
        "country": country_data['meta']['country'],
        "country_code": country_data['meta']['country_code'],
        "country_flag": country_data['meta'].get('country_flag', ''), # Keep for backward compatibility, but will be empty
        "currency": country_data['meta'].get('currency', ''), # Keep for backward compatibility, but will be empty
        "street_address": address['Street'],
        "street_name": address['Street'], # Map to Street for now, as no separate street_name
        "building_number": "", # No direct equivalent, keep empty
        "city": address['City/Town'],
        "state": address['State/Province/Region'],
        "postal_code": address['Zip/Postal Code'],
        "time_zone_offset": "", # No direct equivalent, keep empty
        "time_zone_description": "", # No direct equivalent, keep empty
    }
