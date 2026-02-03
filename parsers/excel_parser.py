"""Excel Parser - Extract data from Excel spreadsheets"""

import openpyxl
from datetime import datetime
from pathlib import Path

def parse_excel(filepath):
    """
    Parse Excel file and extract sheet data

    Args:
        filepath: Path to Excel file

    Returns:
        dict: Parsed Excel data
    """
    result = {
        'filename': Path(filepath).name,
        'file_type': 'excel',
        'parsed_at': datetime.now().isoformat(),
        'sheets': [],
        'metadata': {}
    }

    try:
        workbook = openpyxl.load_workbook(filepath, data_only=True)

        # Extract metadata
        result['metadata'] = {
            'total_sheets': len(workbook.sheetnames),
            'sheet_names': workbook.sheetnames
        }

        # Extract data from each sheet
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]

            sheet_data = {
                'name': sheet_name,
                'rows': sheet.max_row,
                'columns': sheet.max_column,
                'data': []
            }

            # Extract all cell values
            for row in sheet.iter_rows(values_only=True):
                # Convert None to empty string and handle other types
                row_data = [
                    '' if cell is None else str(cell) if not isinstance(cell, (str, int, float)) else cell
                    for cell in row
                ]
                sheet_data['data'].append(row_data)

            result['sheets'].append(sheet_data)

        workbook.close()

    except Exception as e:
        result['error'] = str(e)

    return result
