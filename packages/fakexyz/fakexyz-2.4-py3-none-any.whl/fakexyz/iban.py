from schwifty import IBAN, exceptions

def generate_random_iban(country_code=None, bank_code=None):
    """
    Generates a random, valid IBAN using schwifty.
    Optionally, specify country_code and bank_code.
    """
    return IBAN.random(country_code=country_code, bank_code=bank_code)

def validate_iban(iban_string):
    """
    Validates an IBAN string using schwifty.
    Returns True if valid, False otherwise.
    """
    try:
        IBAN(iban_string)
        return True
    except exceptions.SchwiftyException:
        return False

def get_iban_info(iban_string):
    """
    Returns detailed information about an IBAN, including validation status,
    messages, and bank data, similar to the user's requested format.
    """
    info = {
        "valid": False,
        "messages": [],
        "iban": iban_string,
        "bankData": {
            "bankCode": "",
            "name": ""
        },
        "checkResults": {
            "bankCode": False
        }
    }

    try:
        iban_obj = IBAN(iban_string)
        info["valid"] = True
        info["iban"] = iban_obj.formatted

        if iban_obj.bank:
            info["bankData"]["bankCode"] = iban_obj.bank.get("bank_code", "")
            info["bankData"]["name"] = iban_obj.bank.get("name", "")
            info["checkResults"]["bankCode"] = True
        else:
            info["messages"].append("Cannot get BIC. No information available.")
            info["checkResults"]["bankCode"] = False

    except exceptions.InvalidCountryCode as e:
        info["messages"].append(f"Invalid Country Code: {e}")
    except exceptions.InvalidLength as e:
        info["messages"].append(f"Invalid Length: {e}")
    except exceptions.InvalidChecksumDigits as e:
        info["messages"].append(f"Invalid Checksum Digits: {e}")
    except exceptions.InvalidBBANChecksum as e:
        info["messages"].append(f"Invalid BBAN Checksum: {e}")
    except exceptions.InvalidStructure as e:
        info["messages"].append(f"Invalid Structure: {e}")
    except exceptions.SchwiftyException as e:
        info["messages"].append(f"IBAN Validation Error: {e}")
    except Exception as e:
        info["messages"].append(f"An unexpected error occurred: {e}")

    return info
