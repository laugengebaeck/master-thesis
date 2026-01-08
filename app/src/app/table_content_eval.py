#!/usr/bin/env python
import sys

import Levenshtein
import pandas as pd
from table_plans.csv_import_export import plan_export_csv
from table_plans.pdf_read import ImageOptimizedPlanReader, PdfTextPlanReader


def calculate_acc_cont(expected: pd.DataFrame, recognized: pd.DataFrame):
    equal_count = 0
    for i in range(recognized.shape[0]):
        if i >= expected.shape[0]:
            break
        for j in range(recognized.shape[1]):
            if j >= expected.shape[1]:
                break
            if str(expected.iat[i, j]) == str(recognized.iat[i, j]):
                equal_count += 1
    return equal_count / (expected.shape[0] * expected.shape[1])


def calculate_acc_ed(expected: pd.DataFrame, recognized: pd.DataFrame):
    edit_distance_sum = 0
    for i in range(recognized.shape[0]):
        if i >= expected.shape[0]:
            break
        for j in range(recognized.shape[1]):
            if j >= expected.shape[1]:
                break
            expected_str = str(expected.iat[i, j])
            recognized_str = str(recognized.iat[i, j])
            edit_distance_sum += Levenshtein.distance(expected_str, recognized_str) / max(
                len(expected_str), len(recognized_str)
            )
    return 1 - edit_distance_sum / (expected.shape[0] * expected.shape[1])


def compare_tables(expected: pd.DataFrame, recognized: pd.DataFrame):
    if expected.shape != recognized.shape:
        print(
            f"Caution, dimensions of tables do not match! (expected: {expected.shape}, recognized: {recognized.shape})"
        )
    acc_cont = calculate_acc_cont(expected, recognized)
    print(f"Acc_Cont = {acc_cont}")
    acc_ed = calculate_acc_ed(expected, recognized)
    print(f"Acc_ED = {acc_ed}")


def main():
    path = sys.argv[1]
    pdf_plan_reader = PdfTextPlanReader()
    image_plan_reader = ImageOptimizedPlanReader(min_confidence=30)
    with open(path, "rb") as plan_file:
        print(f"Evaluating {path}...")
        pdf = plan_file.read()
        tables_expected = pdf_plan_reader.read_tables(pdf)
        tables_recognized = image_plan_reader.read_tables(pdf)
        type = path.split("/")[-1].split("_")[1]
        plan_export_csv(tables_recognized, type, path)
        plan_export_csv(tables_expected, f"{type}_expected", path)
        if len(tables_expected) != len(tables_recognized):
            print(
                f"Number of expected tables ({len(tables_expected)}) does not match number of recognized tables ({len(tables_recognized)})!"
            )
            return
        for i in range(len(tables_expected)):
            print(f"Table {i+1}:")
            compare_tables(tables_expected[i], tables_recognized[i])
            input()
        print()


if __name__ == "__main__":
    main()
