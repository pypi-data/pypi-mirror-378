# coding=utf-8

import os
from typing import Optional

from .core._base import standardize_path
from .core.update_json import load_json_data, update_json_file
from .tools.generate_dict import GenerateDataDict
from .tools.write_dict import WriteDataToMd


def main_generate_md_files(
    path_json: str,
    path_output: str,
    path_spidered_bibs: Optional[str] = None,
    for_vue: bool = True,
    conferences_or_journals: Optional[str] = None,
    keywords_category_name: str = ""
) -> None:
    """
    Generate markdown files for conferences and journals.

    Args:
        path_json: Path to JSON data file
        path_output: Output directory for markdown files
        path_spidered_bibs: Directory containing crawled BibTeX files
        for_vue: Whether to generate Vue-compatible format
        conferences_or_journals: Specify 'conferences' or 'journals', None for both
        keywords_category_name: The category name of keywords
    """
    # Standardize all paths
    path_json = standardize_path(path_json)
    path_output = standardize_path(path_output)
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

        # Generate data dictionaries
        path_spidered_cj = os.path.join(path_spidered_bibs, cj.title())
        generater = GenerateDataDict(cj, ia, json_dict, for_vue, path_spidered_cj)
        publisher_meta_dict, publisher_abbr_meta_dict, keyword_abbr_meta_dict = generater.generate()
        if not (publisher_meta_dict and publisher_abbr_meta_dict and keyword_abbr_meta_dict):
            continue

        # Initialize writer and save all markdown files
        _path_output = os.path.join(path_output, f"{cj.title()}")
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
