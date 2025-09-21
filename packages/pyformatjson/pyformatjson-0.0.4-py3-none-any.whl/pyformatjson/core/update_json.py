# coding=utf-8

import json
import os
from typing import Any, Dict

from ._base import split_data_list, split_text_by_length


def load_json_data(path_json: str, filename: str) -> Dict:
    """Load JSON data from a specified file.

    This function attempts to load JSON data from a file located in the specified
    directory. If the file doesn't exist or there's an error loading it, an empty
    dictionary is returned.

    Args:
        path_json (str): Directory path containing the JSON file.
        filename (str): Name of the JSON file (with .json extension).

    Returns:
        Dict: The loaded JSON data as a dictionary, or empty dict if file not found
            or error occurs.

    Example:
        >>> load_json_data("/data", "conferences")
        {"publisher1": {"conferences": {...}}}
    """
    try:
        file_path = os.path.join(path_json, filename)
        if not os.path.exists(file_path):
            return {}

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}


def update_json_file(full_json_cj: str, conferences_or_journals: str) -> Dict[str, Any]:
    """Update and format JSON file containing conference/journal data.

    This function loads JSON data, processes and formats text fields by splitting
    long text into appropriate lengths, checks for duplicate abbreviations, and
    saves the updated data back to the file.

    Args:
        full_json_cj (str): Full path to the conferences/journals JSON file
        conferences_or_journals (str): Type of publication ('conferences' or 'journals').

    Returns:
        Dict[str, Any]: Processed JSON data dictionary.
    """
    # Load Json Data
    json_dict = load_json_data(os.path.dirname(full_json_cj), os.path.basename(full_json_cj))

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
        with open(full_json_cj, "w", encoding="utf-8") as f:
            f.write(json.dumps(json_dict, indent=4, sort_keys=True, ensure_ascii=True))

    return json_dict


def _check_duplicate_abbr(json_dict: Dict[str, Any], conferences_or_journals: str) -> None:
    """Check for duplicate abbreviations in the data.

    This function validates that there are no duplicate abbreviations within
    the same publication type across all publishers.

    Args:
        json_dict (Dict[str, Any]): JSON data dictionary containing publication information.
        conferences_or_journals (str): Type of publication ('conferences' or 'journals').

    Raises:
        ValueError: If duplicate abbreviations are found in the data.

    Example:
        >>> _check_duplicate_abbr(data, "conferences")
        # Raises ValueError if "ICML" appears twice in conferences
    """
    abbr_list = []

    for pub in json_dict:
        if conferences_or_journals in json_dict[pub]:
            for abbr in json_dict[pub][conferences_or_journals]:
                if abbr in abbr_list:
                    raise ValueError(f"Duplicate abbreviation: {abbr} in {conferences_or_journals} {pub}")
                abbr_list.append(abbr)

    return None
