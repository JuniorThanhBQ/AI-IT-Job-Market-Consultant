from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pandas as pd # type: ignore[import-untyped]

from scripts.test_case_report.config import ISSUE_TITLE_PREFIX, TestCase


class TestCaseParser:
    REQUIRED_COLUMNS: ClassVar[set[str]] = {
        "Test case ID",
        "Test case name",
        "Test case procedure",
        "Expected results",
        "Actual results",
        "Status",
        "AI test results",
        "AI Status",
        "Reference",
        "Note",
    }

    COLUMN_MAPPING: ClassVar[dict[str, str]] = {
        "Test case ID": "test_case_id",
        "Test case name": "name",
        "Test case procedure": "procedure",
        "Expected results": "expected_result",
        "Actual results": "actual_result",
        "Status": "status",
        "AI test results": "ai_result",
        "AI Status": "ai_status",
        "Reference": "reference",
        "Note": "note",
    }

    def validate_columns(self, df: pd.DataFrame, sheet_name: str) -> None:
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(
                f"Sheet '{sheet_name}' is missing required columns: {sorted(missing)}"
            )

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=self.COLUMN_MAPPING)
        text_columns = [
            "test_case_id",
            "name",
            "procedure",
            "expected_result",
            "actual_result",
            "status",
            "ai_result",
            "ai_status",
            "reference",
            "note",
        ]
        df = df[text_columns]

        for column in text_columns:
            df[column] = df[column].fillna("").astype(str).str.strip()

        return df

    def find_test_sheets(self, excel: pd.ExcelFile) -> list[str]:
        sheets = []
        for sheet in excel.sheet_names:
            if sheet.strip().lower().startswith("test"):
                sheets.append(sheet)

        if not sheets:
            raise ValueError(
                f"No sheet starting with 'test' found. "
                f"Available sheets: {excel.sheet_names}"
            )

        return sheets

    def find_header_row(self, excel: pd.ExcelFile, sheet_name: str) -> int:
        raw = pd.read_excel(excel, sheet_name=sheet_name, header=None)

        for idx, row in raw.iterrows():
            cell_values = {str(v).strip() for v in row if pd.notna(v)}
            if self.REQUIRED_COLUMNS.issubset(cell_values):
                return int(str(idx))

        raise ValueError(
            f"Sheet '{sheet_name}': could not find a header row containing "
            f"all required columns: {sorted(self.REQUIRED_COLUMNS)}"
        )

    def parse(self, file_path: str | Path) -> list[TestCase]:
        results: list[TestCase] = []

        with pd.ExcelFile(file_path) as excel:
            sheets = self.find_test_sheets(excel)

            for sheet_name in sheets:
                header_row = self.find_header_row(excel, sheet_name)
                df = pd.read_excel(excel, sheet_name=sheet_name, header=header_row)
                self.validate_columns(df, sheet_name)
                df = self.normalize(df)
                for row in df.to_dict(orient="records"):
                    results.append(TestCase(**row, sheet=sheet_name))

        return results


def build_issue_title(test_case: TestCase) -> str:
    return f"{ISSUE_TITLE_PREFIX} {test_case.test_case_id} - {test_case.name}"


def build_issue_body(test_case: TestCase) -> str:
    return (
        f"## Bug Report\n\n"
        f"**Test Case ID:** `{test_case.test_case_id}`  \n"
        f"**Sheet:** `{test_case.sheet}`  \n"
        f"**Reference:** {test_case.reference or '_N/A_'}  \n\n"
        f"### Procedure\n{test_case.procedure or '_N/A_'}\n\n"
        f"### Expected Result\n{test_case.expected_result or '_N/A_'}\n\n"
        f"### Actual Result\n{test_case.actual_result or '_N/A_'}\n\n"
        f"### AI Test Result\n{test_case.ai_result or '_N/A_'}  \n"
        f"**AI Status:** `{test_case.ai_status or 'N/A'}`\n\n"
        f"### Note\n{test_case.note or '_N/A_'}\n"
    )
