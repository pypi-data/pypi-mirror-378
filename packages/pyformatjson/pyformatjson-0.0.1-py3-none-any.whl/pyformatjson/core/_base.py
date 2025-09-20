# coding=utf-8

import os
import re
from typing import List


def split_text_by_length(text, max_length=120) -> List[str]:
    lines = []
    while text:
        if len(text) <= max_length:
            lines.append(text)
            break

        split_pos = text.rfind(" ", 0, max_length + 1)
        if split_pos == -1:
            split_pos = max_length

        line = text[:split_pos]
        lines.append(line)

        text = text[split_pos:]

    new_lines = []
    for line in lines:
        new_lines.append(line)
    return new_lines


def split_data_list(
    split_pattern: str, data_list: List[str], last_next: str = "next"
) -> List[str]:
    r"""Split data list according to the split pattern.

    The capturing parentheses must be used in the pattern, such as `(\n)`.

    Args:
        split_pattern (str): split pattern.
        data_list (List[str]): data list.
        last_next (str): "next" or "last".

    Returns:
        List[str]: new data list.

    Examples:
        split_pattern = r"(\n)", last_next = "next" or "last".
    """
    new_data_list = []
    for line in data_list:
        split_list = re.split(split_pattern, line)
        list_one = split_list[0: len(split_list): 2]
        list_two = split_list[1: len(split_list): 2]

        temp = []
        if last_next == "next":
            list_two.insert(0, "")
            temp = [list_two[i] + list_one[i] for i in range(len(list_one))]
        if last_next == "last":
            list_two.append("")
            temp = [list_one[i] + list_two[i] for i in range(len(list_one))]
        new_data_list.extend(temp)
    new_data_list = [line for line in new_data_list if line.strip()]
    return new_data_list


def standardize_path(path_input: str) -> str:
    path_input = os.path.expandvars(os.path.expanduser(path_input))
    if not os.path.exists(path_input):
        os.makedirs(path_input)
    return path_input


def sort_strings_with_embedded_numbers(s: str) -> List[str]:
    re_digits = re.compile(r"(\d+)")
    pieces = re_digits.split(s)
    pieces[1::2] = map(int, pieces[1::2])
    return pieces


def sort_int_str(str_int: List[str], reverse: bool = False) -> List[str]:
    return sorted(str_int, key=sort_strings_with_embedded_numbers, reverse=reverse)


class IterateSortDict(object):
    def __init__(self, reverse: bool = False) -> None:
        self.reverse = reverse

    def dict_update(self, old):
        """Update."""
        old = self.dict_sort_iteration(old)
        old = self.dict_sort(old)
        return old

    def dict_sort_iteration(self, old: dict):
        """Sort."""
        for key in old:
            if isinstance(old[key], dict):
                old[key] = self.dict_update(old[key])
        return old

    def dict_sort(self, old: dict):
        """Sort."""
        return {k: old[k] for k in sort_int_str(list(old.keys()), self.reverse)}
