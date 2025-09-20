# coding=utf-8

import json
import os
from typing import Optional

from .core._base import standardize_path
from .core.update_json import load_json_data, update_json_file
from .tools.generate_dict import GenerateDataDict
from .tools.write_dict import WriteDataToMd


def main_generate_md_files(
    path_json: str,
    path_output_md: str,
    path_output_simplified_json: str,
    path_spidered_bibs: Optional[str] = None,
    for_vue: bool = True,
    conferences_or_journals: Optional[str] = None,
    keywords_category_name: str = "",
) -> None:
    """Generate markdown files for conferences and journals.

    This function processes JSON data containing conference and journal information,
    generates various markdown documentation files, and creates simplified JSON outputs.
    It supports both conference and journal processing with customizable keyword categories.

    Args:
        path_json (str): Path to the input JSON data file containing publication information.
        path_output_md (str): Output directory path where markdown files will be saved.
        path_output_simplified_json (str): Output directory path for simplified JSON files.
        path_spidered_bibs (Optional[str], optional): Directory containing crawled BibTeX files.
            Defaults to None.
        for_vue (bool, optional): Whether to generate Vue.js-compatible format for date calculations.
            Defaults to True.
        conferences_or_journals (Optional[str], optional): Specify 'conferences' or 'journals' to
            process only one type, or None to process both. Defaults to None.
        keywords_category_name (str, optional): The category name for keywords filtering.
            Defaults to "".

    Returns:
        None: This function does not return a value.

    Raises:
        FileNotFoundError: If the input JSON file or required directories are not found.
        ValueError: If there are issues with the data format or duplicate abbreviations.

    Example:
        >>> main_generate_md_files(
        ...     path_json="/data/publications.json",
        ...     path_output_md="/output/markdown",
        ...     path_output_simplified_json="/output/json",
        ...     for_vue=True,
        ...     conferences_or_journals="conferences"
        ... )
    """
    # Standardize all paths
    path_json = standardize_path(path_json)
    path_output_md = standardize_path(path_output_md)
    path_output_simplified_json = standardize_path(path_output_simplified_json)

    path_spidered_bibs = standardize_path(path_spidered_bibs) if path_spidered_bibs else ""

    # Process keyword category name and load data
    keywords_category_name = keywords_category_name.lower().strip() if keywords_category_name else ""
    category_prefix = f"{keywords_category_name}_" if keywords_category_name else ""
    keywords_list = load_json_data(path_json, "keywords").get(f"{category_prefix}keywords", [])

    # Validate data availability
    if not keywords_list or not keywords_category_name:
        keywords_list, keywords_category_name = [], ""

    # Process both conferences and journals
    for cj, ia in zip(["conferences", "journals"], ["inproceedings", "article"]):
        # Skip if specific type requested and doesn't match
        if conferences_or_journals and conferences_or_journals.lower() != cj:
            continue

        # Update JSON data
        json_dict = update_json_file(path_json, cj)
        if not json_dict:
            continue

        # Simplify JSON data
        simplify_json(json_dict, cj, path_output_simplified_json)

        # Generate data dictionaries
        path_spidered_cj = os.path.join(path_spidered_bibs, cj.title())
        generater = GenerateDataDict(cj, ia, json_dict, for_vue, path_spidered_cj)
        publisher_meta_dict, publisher_abbr_meta_dict, keyword_abbr_meta_dict = generater.generate()
        if not (publisher_meta_dict and publisher_abbr_meta_dict and keyword_abbr_meta_dict):
            continue

        # Initialize writer and save all markdown files
        _path_output = os.path.join(path_output_md, f"{cj.title()}")
        save_data = WriteDataToMd(
            cj, ia, publisher_meta_dict, publisher_abbr_meta_dict, keyword_abbr_meta_dict, _path_output
        )
        # Save various documentation files
        save_data.save_introductions()
        save_data.save_categories(keywords_category_name, keywords_list)
        save_data.save_categories_separate_keywords()

        save_data.save_publishers()
        save_data.save_publishers_separate_abbrs()

        save_data.save_statistics(keywords_category_name, keywords_list)
        save_data.save_statistics_separate_abbrs()

    return None


def simplify_json(json_dict, cj: str, output_dir: str) -> None:
    """Simplify JSON dictionary by extracting only essential fields.

    This function creates a simplified version of the JSON dictionary containing
    only the names_abbr and names_full fields for each publisher and publication type.
    The simplified data is saved to a new JSON file in the specified output directory.

    Args:
        json_dict (dict): The original JSON dictionary containing publication data.
        cj (str): The type of publication, either 'conferences' or 'journals'.
        output_dir (str): Directory path where the simplified JSON file will be saved.

    Returns:
        None: This function does not return a value.

    Note:
        The function creates a new JSON file named '{cj}.json' in the output directory.
        Only the 'names_abbr' and 'names_full' fields are preserved in the simplified version.

    Example:
        >>> simplify_json(
        ...     json_dict=publication_data,
        ...     cj="conferences",
        ...     output_dir="/output/simplified"
        ... )
    """
    new_json_dict = {}
    for publisher in json_dict:
        for abbr in json_dict[publisher][cj.lower()]:
            names_abbr = json_dict[publisher][cj.lower()][abbr].get("names_abbr", [])
            names_full = json_dict[publisher][cj.lower()][abbr].get("names_full", [])

            new_json_dict.setdefault(publisher, {}).setdefault(cj.lower(), {}).setdefault(abbr, {}).update(
                {"names_abbr": names_abbr, "names_full": names_full}
            )

    # Save updated JSON
    if new_json_dict:
        path_file = os.path.join(output_dir, f"{cj}.json")
        with open(path_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(new_json_dict, indent=4, sort_keys=True, ensure_ascii=True))

    return None
