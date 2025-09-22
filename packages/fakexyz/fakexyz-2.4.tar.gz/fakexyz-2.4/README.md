# FakeXYZ - Comprehensive Usage Guide

FakeXYZ is a versatile Python library designed to generate realistic-looking fake user and address information for a wide range of countries. It's an invaluable tool for developers and testers who need to populate databases, anonymize sensitive data, or create mock data for application testing and development.

## Features

*   **Multi-country Support**: Generate data tailored to the specifics of numerous countries, including addresses, names, and other localized information.
*   **Random Address Generation**: Obtain complete address details such as street names, building numbers, cities, states/provinces, postal codes, and timezones.
*   **User Information**: Generate fake personal profiles including names, genders, phone numbers, and avatar URLs.
*   **Intelligent Country Suggestions**: The library provides smart suggestions for country names and codes, helping users correct typos and discover supported regions. It prioritizes exact matches, highly confident fuzzy matches, and prefix-based suggestions.

## Installation

You can easily install FakeXYZ using pip, the Python package installer. It's recommended to install it in a virtual environment to manage dependencies effectively.

```bash
pip install fakexyz
```

If you encounter performance warnings related to `fuzzywuzzy`, you can install `python-Levenshtein` for a faster pure-Python implementation:

```bash
pip install python-Levenshtein
```

## Basic Usage: Importing FakeXYZ

To start using the library, you need to import the `FakeXYZ` class from the `fakexyz` package:

```python
from fakexyz import FakeXYZ

# Create an instance of the FakeXYZ generator
xyz = FakeXYZ()
```

## Generating Random Addresses

You can generate a single random address or multiple addresses, optionally specifying a country.

### Get a Single Random Address

To get a random address, simply call `get_random_address()`. If no country is specified, a random country will be chosen.

```python
# Get a random address from any supported country
address = xyz.get_random_address()
print(address)

# Example Output:
# {
#     'country': 'United States',
#     'country_code': 'US',
#     'country_flag': '', # No longer directly available in address data
#     'currency': '', # No longer directly available in address data
#     'name': 'Gisselle McLaughlin',
#     'gender': 'female',
#     'phone_number': '(504) 733-0254',
#     'street_address': '5606 Jefferson Hwy',
#     'street_name': '5606 Jefferson Hwy', # Mapped from 'Street'
#     'building_number': '', # No direct equivalent
#     'city': 'New Orleans',
#     'state': 'Louisiana',
#     'postal_code': '70123',
#     'time_zone': '', # No direct equivalent
#     'description': '', # No direct equivalent
#     'avatar_url': '', # No direct equivalent
#     'latitude': '29.945541',
#     'longitude': '-90.184308',
#     '
```

### Get a Random Address for a Specific Country

You can specify a country by its full name or its 2-letter ISO country code (case-insensitive).

```python
# Get a random address for the United States using its code
us_address = xyz.get_random_address(country="US")
print(us_address)

# Get a random address for Bangladesh using its full name
bd_address = xyz.get_random_address(country="Bangladesh")
print(bd_address)

# Get a random address for Germany using its code (case-insensitive)
de_address = xyz.get_random_address(country="de")
print(de_address)
```

### Get Multiple Random Addresses

Use `get_random_addresses()` to generate a list of addresses. You can specify the `count` and optionally the `country`.

```python
# Get 3 random addresses from any supported country
multiple_addresses = xyz.get_random_addresses(count=3)
for addr in multiple_addresses:
    print(addr['country'], addr['city'])

# Get 2 random addresses specifically from Canada
ca_addresses = xyz.get_random_addresses(count=2, country="CA")
for addr in ca_addresses:
    print(addr['name'], addr['street_address'])
```

## Handling Incorrect Country Input and Suggestions

FakeXYZ provides intelligent suggestions if the country input is not recognized.

*   **High-Confidence Fuzzy Match**: If your input is a common typo for an existing country, it will suggest the most likely correct country.

    ```python
    try:
        address = xyz.get_random_address(country="bangldesh") # Typo
    except ValueError as e:
        print(e)
    # Expected output: Country 'bangldesh' not found. Did you mean?
    # 🇧🇩 Bangladesh (<code>BD</code>)
    ```

*   **Prefix-Based Suggestions**: If your input starts with a character or a short sequence that matches multiple countries, it will suggest all relevant countries. This is particularly useful for exploring options.

    ```python
    try:
        address = xyz.get_random_address(country="g") # Single character
    except ValueError as e:
        print(e)
    # Expected output: Country 'g' not found. Did you mean?
    # 🇩🇪 Germany (<code>DE</code>)
    # 🇬🇧 United Kingdom (<code>GB</code>)
    # 🇬🇪 Georgia (<code>GE</code>)
    # 🇬🇭 Ghana (<code>GH</code>)
    # 🇬🇱 Greenland (<code>GL</code>)
    # 🇬🇷 Greece (<code>GR</code>)
    # 🇬🇹 Guatemala (<code>GT</code>)

    try:
        address = xyz.get_random_address(country="im") # Two characters
    except ValueError as e:
        print(e)
    # Expected output: Country 'im' not found. Did you mean?
    # 🇮🇩 Indonesia (<code>ID</code>)
    # 🇮🇳 India (<code>IN</code>)
    # 🇮🇶 Iraq (<code>IQ</code>)
    # 🇮🇪 Ireland (<code>IE</code>)
    # 🇮🇱 Israel (<code>IL</code>)
    # 🇮🇸 Iceland (<code>IS</code>)
    # 🇮🇹 Italy (<code>IT</code>)
    ```

*   **No Close Match**: If no reasonable suggestions can be found, a general message will be displayed.

    ```python
    try:
        address = xyz.get_random_address(country="zz") # No close match
    except ValueError as e:
        print(e)
    # Expected output: Country 'zz' not found.
    # Did you mean?
    # Please check the supported countries list using the `!country` command.
    ```

## Listing Supported Countries

FakeXYZ currently supports **86** countries. Here is a comprehensive list of all supported countries with their flags and 2-letter ISO codes:

*   🇦🇫 Afghanistan (AF)
*   🇦🇱 Albania (AL)
*   🇩🇿 Algeria (DZ)
*   🇦🇮 Anguilla (AI)
*   🇦🇶 Antarctica (AQ)
*   🇦🇷 Argentina (AR)
*   🇦🇲 Armenia (AM)
*   🇦🇺 Australia (AU)
*   🇦🇹 Austria (AT)
*   🇦🇿 Azerbaijan (AZ)
*   🇧🇩 Bangladesh (BD)
*   🇧🇲 Bermuda (BM)
*   🇧🇴 Bolivia (BO)
*   🇧🇹 Bhutan (BT)
*   🇧🇷 Brazil (BR)
*   🇧🇬 Bulgaria (BG)
*   🇰🇭 Cambodia (KH)
*   🇨🇲 Cameroon (CM)
*   🇨🇦 Canada (CA)
*   🇨🇱 Chile (CL)
*   🇨🇳 China (CN)
*   🇨🇴 Colombia (CO)
*   🇨🇿 Czechia (CZ)
*   🇩🇰 Denmark (DK)
*   🇪🇬 Egypt (EG)
*   🇫🇮 Finland (FI)
*   🇫🇷 France (FR)
*   🇬🇪 Georgia (GE)
*   🇩🇪 Germany (DE)
*   🇬🇭 Ghana (GH)
*   🇬🇷 Greece (GR)
*   🇬🇱 Greenland (GL)
*   🇬🇹 Guatemala (GT)
*   🇭🇰 Hong Kong (HK)
*   🇮🇸 Iceland (IS)
*   🇮🇳 India (IN)
*   🇮🇩 Indonesia (ID)
*   🇮🇶 Iraq (IQ)
*   🇮🇪 Ireland (IE)
*   🇮🇱 Israel (IL)
*   🇮🇹 Italy (IT)
*   🇯🇵 Japan (JP)
*   🇯🇴 Jordan (JO)
*   🇰🇿 Kazakhstan (KZ)
*   🇰🇪 Kenya (KE)
*   🇧🇭 Kingdom of Bahrain (BH)
*   🇧🇪 Kingdom of Belgium (BE)
*   🇱🇧 Lebanon (LB)
*   🇲🇾 Malaysia (MY)
*   🇲🇻 Maldives (MV)
*   🇲🇷 Mauritania (MR)
*   🇲🇽 Mexico (MX)
*   🇲🇦 Morocco (MA)
*   🇲🇲 Myanmar (MM)
*   🇳🇵 Nepal (NP)
*   🇳🇱 Netherlands (NL)
*   🇳🇿 New Zealand (NZ)
*   🇳🇪 Niger (NE)
*   🇳🇬 Nigeria (NG)
*   🇳🇴 Norway (NO)
*   🇴🇲 Oman (OM)
*   🇵🇰 Pakistan (PK)
*   🇵🇸 Palestine (PS)
*   🇵🇦 Panama (PA)
*   🇵🇪 Peru (PE)
*   🇵🇭 Philippines (PH)
*   🇵🇱 Poland (PL)
*   🇵🇹 Portugal (PT)
*   🇶🇦 Qatar (QA)
*   🇷🇴 Romania (RO)
*   🇷🇺 Russia (RU)
*   🇸🇲 San Marino (SM)
*   🇸🇦 Saudi Arabia (SA)
*   🇸🇬 Singapore (SG)
*   🇿🇦 South Africa (ZA)
*   🇰🇷 South Korea (KR)
*   🇪🇸 Spain (ES)
*   🇱🇰 Sri Lanka (LK)
*   🇸🇩 Sudan (SD)
*   🇸🇪 Sweden (SE)
*   🇨🇭 Switzerland (CH)
*   🇹🇼 Taiwan (TW)
*   🇹🇿 Tanzania (TZ)
*   🇹🇭 Thailand (TH)
*   🇹🇷 Turkiye (TR)
*   🇺🇬 Uganda (UG)
*   🇺🇦 Ukraine (UA)
*   🇦🇪 United Arab Emirates (AE)
*   🇬🇧 United Kingdom (GB)
*   🇺🇸 United States (US)
*   🇻🇪 Venezuela (VE)
*   🇻🇳 Vietnam (VN)
*   🇾🇪 Yemen (YE)

You can also programmatically retrieve a list of all countries currently supported by the library:

```python
from fakexyz import FakeXYZ

xyz = FakeXYZ()
countries = xyz.get_available_countries()
print("Supported Countries:", countries)

# Example Output:
# Supported Countries: ['Afghanistan', 'Albania', 'Algeria', ..., 'Yemen', 'Zambia']
```

## Available Data Fields

The `get_random_address` method returns a dictionary containing the following fields:

*   `country`: Full name of the country (e.g., "United States")
*   `country_code`: 2-letter ISO country code (e.g., "US")
*   `country_flag`: Emoji flag of the country (e.g., "🇺🇸") - *Note: This field will be empty as flags are no longer in the raw data.*
*   `currency`: Currency code (e.g., "USD") - *Note: This field will be empty as currency is no longer in the raw data.*
*   `name`: Full name of the person (e.g., "John Doe") - *Mapped from 'Full Name' in raw data.*
*   `gender`: Gender of the person (e.g., "Male", "Female")
*   `phone_number`: Phone number (e.g., "+1-555-123-4567") - *Mapped from 'Phone Number' in raw data.*
*   `street_address`: Full street address (e.g., "123 Main St") - *Mapped from 'Street' in raw data.*
*   `street_name`: Name of the street (e.g., "Main St") - *Currently mapped from 'Street' in raw data as no separate field exists.*
*   `building_number`: Building or house number - *No direct equivalent in raw data, will be empty.*
*   `city`: City (e.g., "Anytown") - *Mapped from 'City/Town' in raw data.*
*   `state`: State or province (e.g., "CA") - *Mapped from 'State/Province/Region' in raw data.*
*   `postal_code`: Postal or ZIP code (e.g., "90210") - *Mapped from 'Zip/Postal Code' in raw data.*
*   `time_zone`: Timezone offset (e.g., "-08:00") - *No direct equivalent in raw data, will be empty.*
*   `description`: Timezone description (e.g., "Pacific Standard Time") - *No direct equivalent in raw data, will be empty.*
*   `avatar_url`: URL to a random avatar image - *No direct equivalent in raw data, will be empty.*
*   `latitude`: Latitude coordinate (e.g., "34.0522")
*   `longitude`: Longitude coordinate (e.g., "-118.2437")
*   `birthday`: Date of birth (e.g., "1990-01-01")
*   `social_security_number`: Social Security Number (e.g., "XXX-XX-XXXX")
*   `credit_card_brand`: Brand of the credit card (e.g., "Visa")
*   `credit_card_number`: Credit card number (e.g., "XXXXXXXXXXXXXXXX")
*   `expire`: Credit card expiration date (e.g., "2025/12")
*   `cvv`: Credit card CVV (e.g., "123")

## IBAN Generation and Validation

FakeXYZ now includes functionality to generate and validate International Bank Account Numbers (IBANs) using the `schwifty` library. This feature supports **42** countries, allowing for robust IBAN operations for a significant number of regions.

The countries currently supported for IBAN generation and validation are:
Andorra, Austria, Belgium, Bosnia and Herzegovina, Bulgaria, Costa Rica, Croatia, Czech Republic, Cyprus, Denmark, Estonia, Finland, France, Germany, Greece, Hungary, Ireland, Iceland, Italy, Israel, Kazakhstan, Latvia, Lithuania, Luxembourg, Moldova, Monaco, Netherlands, Norway, Poland, Portugal, Romania, Saudi Arabia, Serbia, Slovakia, Slovenia, South Africa, Spain, Sweden, Switzerland, Turkiye, Ukraine, United Arab Emirates, United Kingdom.

### Generate a Random IBAN

You can generate a random, valid IBAN, optionally specifying a country code or bank code.

```python
from fakexyz.iban import generate_random_iban

# Generate a random IBAN from any supported country
random_iban = generate_random_iban()
print(f"Random IBAN: {random_iban.formatted}")

# Generate a German IBAN
german_iban = generate_random_iban(country_code="DE")
print(f"German IBAN: {german_iban.formatted}")

# Generate a German IBAN from a specific bank (if supported by schwifty's registry)
# Note: Not all bank codes are available for random generation.
# lloyds_iban = generate_random_iban(country_code="GB", bank_code="LOYD")
# print(f"Lloyds Bank IBAN: {lloyds_iban.formatted}")
```

### Validate an IBAN

You can validate an IBAN string to check its correctness.

```python
from fakexyz.iban import validate_iban

# Validate a correct IBAN
valid_iban_string = "DE89370400440532013000"
is_valid = validate_iban(valid_iban_string)
print(f"Is '{valid_iban_string}' valid? {is_valid}")

# Validate an incorrect IBAN
invalid_iban_string = "DE89370400440532013001" # Incorrect checksum
is_invalid = validate_iban(invalid_iban_string)
print(f"Is '{invalid_iban_string}' valid? {is_invalid}")
```

### Get Detailed IBAN Information

Retrieve comprehensive details about an IBAN, including its validation status, any messages, and associated bank data.

```python
from fakexyz.iban import get_iban_info
import json

# Get info for a valid German IBAN
iban_info = get_iban_info("DE89370400440532013000")
print(json.dumps(iban_info, indent=2, ensure_ascii=False))

# Get info for an invalid IBAN
invalid_iban_info = get_iban_info("DE89370400440532013001")
print(json.dumps(invalid_iban_info, indent=2, ensure_ascii=False))

# Get info for an IBAN where bank data might not be in schwifty's registry
generic_gb_iban = "GB33BUKB20201555555555"
generic_gb_info = get_iban_info(generic_gb_iban)
print(json.dumps(generic_gb_info, indent=2, ensure_ascii=False))
```

## Contributing

Contributions to FakeXYZ are highly encouraged! If you have suggestions for new features, bug reports, or want to add data for more countries, please feel free to:

1.  **Submit an Issue**: For bug reports or feature requests, open an issue on the GitHub repository.
2.  **Submit a Pull Request**: If you've implemented a new feature or fixed a bug, submit a pull request. Ensure your code adheres to the project's style and includes relevant tests.

## License

This project is open-source and licensed under the MIT License. See the `LICENSE.txt` file in the repository for full details.
