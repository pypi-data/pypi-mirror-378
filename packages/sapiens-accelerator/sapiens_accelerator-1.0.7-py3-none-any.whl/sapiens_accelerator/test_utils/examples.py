"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import os
from typing import List
def get_function_contents_by_name(lines: List[str], name: str):
    if name != "training_function" and name != "main": raise ValueError(f"Incorrect function name passed: {name}, choose either 'main' or 'training_function'")
    good_lines, found_start = [], False
    for line in lines:
        if not found_start and f"def {name}" in line:
            found_start = True
            good_lines.append(line)
            continue
        if found_start:
            if name == "training_function" and "def main" in line: return good_lines
            if name == "main" and "if __name__" in line: return good_lines
            good_lines.append(line)
def clean_lines(lines: List[str]): return [line for line in lines if not line.lstrip().startswith("#") and line != "\n"]
def compare_against_test(base_filename: str, feature_filename: str, parser_only: bool, secondary_filename: str = None):
    with open(base_filename) as f: base_file_contents = f.readlines()
    with open(os.path.abspath(os.path.join("examples", "nlp_example.py"))) as f: full_file_contents = f.readlines()
    with open(feature_filename) as f: feature_file_contents = f.readlines()
    if secondary_filename is not None:
        with open(secondary_filename) as f: secondary_file_contents = f.readlines()
    if parser_only:
        base_file_func = clean_lines(get_function_contents_by_name(base_file_contents, "main"))
        full_file_func = clean_lines(get_function_contents_by_name(full_file_contents, "main"))
        feature_file_func = clean_lines(get_function_contents_by_name(feature_file_contents, "main"))
        if secondary_filename is not None: secondary_file_func = clean_lines(get_function_contents_by_name(secondary_file_contents, "main"))
    else:
        base_file_func = clean_lines(get_function_contents_by_name(base_file_contents, "training_function"))
        full_file_func = clean_lines(get_function_contents_by_name(full_file_contents, "training_function"))
        feature_file_func = clean_lines(get_function_contents_by_name(feature_file_contents, "training_function"))
        if secondary_filename is not None: secondary_file_func = clean_lines(get_function_contents_by_name(secondary_file_contents, "training_function"))
    _dl_line = "train_dataloader, eval_dataloader = get_dataloaders(accelerator, batch_size)\n"
    new_feature_code = []
    passed_idxs = []
    it = iter(feature_file_func)
    for i in range(len(feature_file_func) - 1):
        if i not in passed_idxs:
            line = next(it)
            if (line not in full_file_func) and (line.lstrip() != _dl_line):
                if "TESTING_MOCKED_DATALOADERS" not in line:
                    new_feature_code.append(line)
                    passed_idxs.append(i)
                else: _ = next(it)
    new_full_example_parts = []
    passed_idxs = []
    for i, line in enumerate(base_file_func):
        if i not in passed_idxs:
            if (line not in full_file_func) and (line.lstrip() != _dl_line):
                if "TESTING_MOCKED_DATALOADERS" not in line:
                    new_full_example_parts.append(line)
                    passed_idxs.append(i)
    diff_from_example = [line for line in new_feature_code if line not in new_full_example_parts]
    if secondary_filename is not None:
        diff_from_two = [line for line in full_file_contents if line not in secondary_file_func]
        diff_from_example = [line for line in diff_from_example if line not in diff_from_two]
    return diff_from_example
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
