# coding=utf-8

import os
from typing import List

from ..core._base import standardize_path
from .generate_dict import conference_journal_header


def conference_journal_informations():
    conference_inf = [
        "!> [List of Upcoming International Conferences](https://internationalconferencealerts.com/all-events.php)\n\n",
        "!> [Conferences in Theoretical Computer Science](https://www.lix.polytechnique.fr/~hermann/conf.php)\n\n"
    ]
    journal_inf = []
    return conference_inf, journal_inf


class WriteDataToMd(object):
    """Class to write publication data to Markdown files."""

    def __init__(
        self,
        conferences_or_journals: str,
        inproceedings_or_article: str,
        publisher_meta_dict: dict,
        publisher_abbr_meta_dict: dict,
        keyword_abbr_meta_dict: dict,
        path_output: str,
    ) -> None:
        """Initialize with publication data and output path."""
        self.cj = conferences_or_journals  # "conferences" or "journals"
        self.ia = inproceedings_or_article  # "inproceedings" or "article"
        self.publisher_meta_dict = publisher_meta_dict
        self.publisher_abbr_meta_dict = publisher_abbr_meta_dict
        self.keyword_abbr_meta_dict = keyword_abbr_meta_dict
        self.path_output = standardize_path(path_output)

        self._default_inf = [
            "- The data for TOP, CCF, CAS, JCR, and IF are sourced from [easyScholar](https://www.easyscholar.cc/).\n\n"
        ]

    def save_introductions(self) -> None:
        """Save introduction file with all conferences/journals list."""
        conference_header, journal_header = conference_journal_header()
        conference_inf, journal_inf = conference_journal_informations()

        data_list = [f"# {self.cj.title()}\n\n"]
        data_list.extend(self._default_inf)

        # Add appropriate headers based on type
        if self.cj.lower() == "conferences":
            data_list.extend(conference_inf)
            data_list.append("|  " + conference_header[0])
            data_list.append("|- " + conference_header[1])
        else:
            data_list.extend(journal_inf)
            data_list.append("|  " + journal_header[0])
            data_list.append("|- " + journal_header[1])

        # Add all publications to table
        idx = 1
        for publisher in self.publisher_abbr_meta_dict:
            for abbr in self.publisher_abbr_meta_dict[publisher]:
                row_info = self.publisher_abbr_meta_dict[publisher][abbr]['row_inf']
                data_list.append(f"|{idx}{row_info}\n")
                idx += 1

        # Write to file
        output_file = os.path.join(self.path_output, f"Introductions_{self.cj.title()}.md")
        with open(output_file, "w") as f:
            f.writelines(data_list)

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def _default_or_customized_keywords(self, keywords_category_name: str, keywords_list: List[str]):
        keywords = list(self.keyword_abbr_meta_dict.keys())

        # Get and sort publication types
        if keywords_category_name and keywords_list:
            _keywords = []
            for keyword in keywords_list:
                if keyword in keywords:
                    _keywords.append(keyword)
            return _keywords
        else:
            # default
            return sorted(keywords)

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def save_categories(self, keywords_category_name: str, keywords_list: List[str]) -> None:
        """Save publications categorized by keywords."""
        conference_header, journal_header = conference_journal_header()
        data_list = [f"# {self.cj.title()}\n\n"]
        data_list.extend(self._default_inf)

        # Add publications for each category
        for keyword in self._default_or_customized_keywords(keywords_category_name, keywords_list):
            data_list.append(f"## {keyword}\n\n")

            # Add appropriate header
            if self.cj == "conferences":
                data_list.extend(conference_header)
            else:
                data_list.extend(journal_header)

            # Add all publications in this category
            for abbr in self.keyword_abbr_meta_dict[keyword]:
                data_list.append(self.keyword_abbr_meta_dict[keyword][abbr]["row_inf"] + "\n")
            data_list.append("\n")

        # Write to file
        category_postfix = f"_{keywords_category_name.title()}" if keywords_category_name else ""
        with open(os.path.join(self.path_output, f"Categories_{self.cj.title()}{category_postfix}.md"), "w") as f:
            f.writelines(data_list)

        return None

    def save_categories_separate_keywords(self) -> None:
        conference_header, journal_header = conference_journal_header()

        # Add publications for each category
        for keyword in self.keyword_abbr_meta_dict:
            data_list = [f"# {keyword}\n\n"]
            data_list.extend(self._default_inf)

            # Add appropriate header
            if self.cj == "conferences":
                data_list.extend(conference_header)
            else:
                data_list.extend(journal_header)

            # Add all publications in this category
            for abbr in self.keyword_abbr_meta_dict[keyword]:
                data_list.append(self.keyword_abbr_meta_dict[keyword][abbr]["row_inf"] + "\n")
            data_list.append("\n")

            # Write keyword-specific file
            path_key = standardize_path(os.path.join(self.path_output, f"Categories_{self.cj.title()}"))
            with open(os.path.join(path_key, f"{keyword.replace(' ', '_')}.md"), "w") as f:
                f.writelines(data_list)

        return None

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def save_publishers(self) -> None:
        """Save publisher overview file with basic information."""
        data_list_pub = [
            f"# Introductions of Publishers and {self.cj.title()}\n\n",
            "| |Publishers|About US|Conferences/Journals|Separate Links|\n",
            "|-|-         |-       |-                   |-             |\n"
        ]
        idx = 1

        # Add each publisher to table
        for pub in self.publisher_meta_dict:
            meta = self.publisher_meta_dict[pub]

            full_name_url, about_url, cj_url, local_url = "", "", "", ""
            if x := meta.get("full_name_url", ""):
                full_name_url = x
            if x := meta.get("url_conferences_or_journals", ""):
                cj_url = x
            if pub_intr_urls := meta.get("urls_about", []):
                about_url = f"[About US]({pub_intr_urls[0]})"

            local_url = f"[{pub}](data/{self.cj.title()}/Publishers_{self.cj.title()}/{pub}.md)"

            # Create table row
            row = f"| {idx} | {full_name_url} | {about_url} | {cj_url} | {local_url} |\n"
            data_list_pub.append(row)
            idx += 1

        # Write to file
        with open(os.path.join(self.path_output, f"Publishers_{self.cj.title()}.md"), "w") as f:
            f.writelines(data_list_pub)
        return None

    def save_publishers_separate_abbrs(self) -> None:
        conference_header, journal_header = conference_journal_header()
        for pub in self.publisher_meta_dict:
            data_list = [f"# {pub}\n\n"]
            data_list.extend(self._default_inf)
            meta = self.publisher_meta_dict[pub]

            # Add about and remarks sections
            for flag in ["txt_remarks", "txt_abouts"]:
                if temps := meta.get(flag, []):
                    temps[-1] = f"{temps[-1].rstrip()}\n\n"
                if temps:
                    data_list.append(f"## {flag.title()}\n\n")
                    data_list.extend(temps)

            # Add each conference/journal abbreviation
            if pub not in self.publisher_abbr_meta_dict:
                continue

            for abbr in self.publisher_abbr_meta_dict[pub]:
                data_list.append(f"## {abbr}\n\n")

                # Add appropriate header
                if self.cj == "conferences":
                    data_list.extend(conference_header)
                else:
                    data_list.extend(journal_header)

                # Add row information
                row_info = self.publisher_abbr_meta_dict[pub][abbr]["row_inf"]
                data_list.append(f'{row_info}\n\n')

                # Add remarks and about for this abbreviation
                for flag in ["txt_remarks", "txt_abouts"]:
                    if temps := self.publisher_abbr_meta_dict[pub][abbr].get(flag, []):
                        temps[-1] = f"{temps[-1].rstrip()}\n\n"
                    if temps:
                        data_list.append(f"### {flag.split('_')[-1].title()}\n\n")
                        data_list.extend(temps)

                # Add statistics if available
                if statistics := self.publisher_abbr_meta_dict[pub][abbr].get("statistics", []):
                    data_list.extend(statistics)
                    data_list.append("\n")

            # Write publisher-specific file
            path_pub = standardize_path(os.path.join(self.path_output, f"Publishers_{self.cj.title()}"))
            with open(os.path.join(path_pub, f"{pub}.md"), "w") as f:
                f.writelines(data_list)

        return None

    # --------- --------- --------- --------- --------- --------- --------- --------- --------- #
    def save_statistics(self, keywords_category_name: str, keywords_list: List[str]) -> None:
        data_list = [
            f"# Statistics of keywords in {self.cj.title()}\n\n",
            "| |keywords|Separate Links|\n",
            "|-|-      |-             |\n"
        ]
        idx = 1

        # Add publications for each category
        for keyword in self._default_or_customized_keywords(keywords_category_name, keywords_list):
            local_url = f"[Link](data/{self.cj.title()}/Statistics_{self.cj.title()}/{keyword.replace(' ', '_')}.md)"

            # Create table row
            row = f"| {idx} | {keyword} | {local_url} |\n"
            data_list.append(row)
            idx += 1

        # Write to file
        category_postfix = f"_{keywords_category_name.title()}" if keywords_category_name else ""
        with open(os.path.join(self.path_output, f"Statistics_{self.cj.title()}{category_postfix}.md"), "w") as f:
            f.writelines(data_list)
        return None

    def save_statistics_separate_abbrs(self) -> None:
        conference_header, journal_header = conference_journal_header()

        # Add publications for each category
        for keyword in self.keyword_abbr_meta_dict:
            data_list = [f"# {keyword}\n\n"]

            for abbr in self.keyword_abbr_meta_dict[keyword]:
                data_list.append(f"## {abbr}\n\n")

                # Add appropriate header
                if self.cj == "conferences":
                    data_list.extend(conference_header)
                else:
                    data_list.extend(journal_header)

                # Add row information
                row_info = self.keyword_abbr_meta_dict[keyword][abbr]["row_inf"]
                data_list.append(f'{row_info}\n\n')

                # Add statistics if available
                if statistics := self.keyword_abbr_meta_dict[keyword][abbr].get("statistics", []):
                    data_list.extend(statistics)
                    data_list.append("\n")

            # Write publisher-specific file
            path_pub = standardize_path(os.path.join(self.path_output, f"Statistics_{self.cj.title()}"))
            with open(os.path.join(path_pub, f"{keyword.replace(' ', '_')}.md"), "w") as f:
                f.writelines(data_list)

        return None
