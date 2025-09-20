# coding=utf-8

import json
import os
from typing import Any, Dict

from ._base import split_data_list, split_text_by_length


def load_json_data(path_json: str, filename: str) -> Dict:
    """Load JSON data from file."""
    try:
        file_path = os.path.join(path_json, f"{filename}.json")
        if not os.path.exists(file_path):
            return {}

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as e:
        print(f"Error loading {filename}.json: {e}")
        return {}


def update_json_file(path_root: str, conferences_or_journals: str) -> Dict[str, Any]:
    """
    Update and format JSON file containing conference/journal data.

    Args:
        path_root (str): Root directory path
        conferences_or_journals (str): Type of publication ('conferences' or 'journals')

    Returns:
        Dict[str, Any]: Processed JSON data
    """
    # Load Json Data
    json_dict = load_json_data(path_root, conferences_or_journals)

    # Process and format text fields in JSON data.
    for pub in json_dict:
        for flag in ["txt_abouts", "txt_remarks"]:
            data_list = [p for p in json_dict[pub].get(flag, []) if p.strip()]
            temps = []
            for line in split_data_list(r"(\n+)", ["".join(data_list)], "next"):
                temps.extend(split_text_by_length(line, 105))
            if temps:
                json_dict[pub].update({flag: temps})

        for abbr in json_dict[pub][conferences_or_journals]:
            for flag in ["txt_abouts", "txt_remarks"]:
                data_list = [i for i in json_dict[pub][conferences_or_journals][abbr].get(flag, []) if i.strip()]
                temps = []
                for line in split_data_list(r"(\n+)", ["".join(data_list)], "next"):
                    temps.extend(split_text_by_length(line, 97))
                if temps:
                    json_dict[pub][conferences_or_journals][abbr].update({flag: temps})

    # Check for duplicate abbreviations
    _check_duplicate_abbr(json_dict, conferences_or_journals)

    # Save updated JSON
    if json_dict:
        path_file = os.path.join(path_root, f"{conferences_or_journals}.json")
        with open(path_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_dict, indent=4, sort_keys=True, ensure_ascii=True))

    return json_dict


def _check_duplicate_abbr(json_dict: Dict[str, Any], conferences_or_journals: str) -> None:
    """
    Check for duplicate abbreviations in the data.

    Args:
        json_dict: JSON data dictionary
        conferences_or_journals (str): Type of publication ('conferences' or 'journals')

    Raises:
        ValueError: If duplicate abbreviations are found
    """
    abbr_list = []

    for pub in json_dict:
        if conferences_or_journals in json_dict[pub]:
            for abbr in json_dict[pub][conferences_or_journals]:
                if abbr in abbr_list:
                    raise ValueError(f"Duplicate abbreviation: {abbr} in {conferences_or_journals} {pub}")
                abbr_list.append(abbr)

    return None
