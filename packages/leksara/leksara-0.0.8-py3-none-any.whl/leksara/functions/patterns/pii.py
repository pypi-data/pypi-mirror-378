"""PII cleaning: remove/replace phone, address, email, id."""
import os
import re
import json
from pathlib import Path

try:
    config_path = Path(__file__).resolve().parent.parent.parent / "resources" / "regex_patterns" / "pii_patterns.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        PII_CONFIG = json.load(f)
except Exception as e:
    print(f"Gagal memuat file konfigurasi: {e}")
    PII_CONFIG = {}

address_config = PII_CONFIG.get("pii_address", {})
email_config = PII_CONFIG.get("pii_email", {})
NIK_config = PII_CONFIG.get("pii_nik", {})
phone_config = PII_CONFIG.get("pii_phone", {})


def replace_phone(text: str, mode: str = "remove") -> str:
    if not isinstance(text, str):
        raise TypeError(f"Input harus berupa string, tetapi menerima tipe {type(text).__name__}")

    allowed_modes = {"remove", "replace"}
    if mode not in allowed_modes:
        raise ValueError(f"Mode '{mode}' tidak valid. Pilihan yang tersedia adalah {list(allowed_modes)}")

    replacement_token = '[PHONE_NUMBER]' if mode == "replace" else ''

    def validate_and_replace(match):
        potential_number = match.group(0)
        cleaned_number = re.sub(r'[-\s]', '', potential_number)

        normalized_number = None
        if cleaned_number.startswith(('+62', '62')):
            normalized_number = '0' + re.sub(r'^\+?62', '', cleaned_number)
        elif cleaned_number.startswith('0'):
            normalized_number = cleaned_number

        if normalized_number and 10 <= len(normalized_number) <= 13:
            return replacement_token

        return potential_number
    
    PHONE_PATTERN = phone_config.get("pattern", "")
    return re.sub(PHONE_PATTERN, validate_and_replace, text)


def replace_address(text: str, mode: str = "remove", **kwargs) -> str:
    if not isinstance(text, str):
        raise TypeError(f"Input harus berupa string, tetapi menerima tipe {type(text).__name__}")

    allowed_modes = {"remove", "replace"}
    if mode not in allowed_modes:
        raise ValueError(f"Mode '{mode}' tidak valid. Pilihan yang tersedia adalah {list(allowed_modes)}")

    replacement_token = '[ADDRESS]' if mode == "replace" else ''

    trigger_config = address_config.get("trigger_pattern", {})
    trigger_pattern = trigger_config.get("pattern", "")
    address_components = address_config.get("components", {})

    if kwargs:
        allowed_keys = {k.replace("pii_addr_", "") for k in address_components.keys()}
        provided_keys = set(kwargs.keys())
        unknown_keys = provided_keys.difference(allowed_keys)
        if unknown_keys:
            raise KeyError(f"Parameter tidak dikenal: {list(unknown_keys)}. Pilihan yang valid adalah: {list(allowed_keys)}")

    if not re.search(trigger_pattern, text, flags=re.IGNORECASE):
        return text

    processed_text = text

    patterns_to_run = []

    if not kwargs:
        patterns_to_run = [v['pattern'] for v in address_components.values()]

    else:
        for component_id, component_data in address_components.items():
            simple_component_name = component_id.replace("pii_addr_", "")
            if kwargs.get(simple_component_name, False):
                patterns_to_run.append(component_data['pattern'])

    for pattern in patterns_to_run:
        processed_text = re.sub(pattern, replacement_token, processed_text, flags=re.IGNORECASE)

    processed_text = re.sub(r'\s{2,}', ' ', processed_text).strip()
    return processed_text


def replace_email(text: str, mode: str = "remove")-> str:
    if not isinstance(text, str):
        raise TypeError(f"Input harus berupa string, tetapi menerima tipe {type(text).__name__}")

    allowed_modes = {"remove", "replace"}
    if mode not in allowed_modes:
        raise ValueError(f"Mode '{mode}' tidak valid. Pilihan yang tersedia adalah {list(allowed_modes)}")

    replacement_token = '[EMAIL]' if mode == "replace" else ''

    EMAIL_PATTERN = email_config.get("pattern", "")
    return re.sub(EMAIL_PATTERN, replacement_token, text)


def replace_id(text: str, mode: str = "remove") -> str:
    if not isinstance(text, str):
        raise TypeError(f"Input harus berupa string, tetapi menerima tipe {type(text).__name__}")

    allowed_modes = {"remove", "replace"}
    if mode not in allowed_modes:
        raise ValueError(f"Mode '{mode}' tidak valid. Pilihan yang tersedia adalah {list(allowed_modes)}")

    replacement_token = '[NIK]' if mode == "replace" else ''

    NIK_PATTERN = NIK_config.get("pattern", "")
    return re.sub(NIK_PATTERN, replacement_token, text)