import os
from datetime import datetime
from typing import Union, List
from abc import ABC

import pdfplumber
from openpyxl.workbook import Workbook

from ready_.model_to_extract import Requisites


class AbstractExtractor(ABC):
    def __init__(self, path: str, page_number: int = 0):
        self.pdf_file = pdfplumber.open(path)
        self.page_number = page_number

    def __del__(self):
        self.pdf_file.close()


class BillingAddressExtractor(AbstractExtractor):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x1_billing_coord = self.pdf_file.pages[self.page_number].width // 3

    def get_billing_address(self):
        resource_link = self.pdf_file.pages[0]
        rects = resource_link.rects[1:3]
        top, bottom = sorted([r['top'] for r in rects])
        result = resource_link.within_bbox(bbox=(0, top, self.x1_billing_coord, bottom))
        # print(result.extract_text())
        return result.extract_text()

    def get_delivery_date(self):
        resource_link = self.pdf_file.pages[0]
        top = resource_link.rects[-1]['top']
        curves = resource_link.curves[-4:]
        bot = max((set([r['top'] for r in curves])))
        left, right = sorted(set([r['x1'] for r in curves]))
        # left top right bottom
        result = resource_link.within_bbox(bbox=(left, top, right, bot))
        return result.extract_text()


class WBWorker:

    columns = {
        "Name": "A", "NIP": "B", "Ulica": "C", "Kod": "D", "Miasto": "E", "email": "F", "telefon": "G",
        "Nazwa_skr": "H", "REGON": "I", "Rabat": "J", "Opis": "K", "Odbiorca": "L", "Nadawca": "M",
        "Kraj": "N"
    }

    def __init__(self, file_name: Union[str, None] = None, path_to_save: Union[str, None] = None):
        self._workbook = Workbook()
        self._sheet = self._workbook.active
        self._file_name = self._create_name() + '.xlsx' if not file_name else file_name
        self._path_to_save = os.path.join(
            os.getcwd(), self._file_name) if not path_to_save else os.path.join(path_to_save, self._file_name)

        self._create_title_row()

    @classmethod
    def _create_name(cls):
        return datetime.utcnow().strftime("%d_%m_%Y__%H_%M")

    def _create_title_row(self):

        length = len(self.columns.items())

        for key, value in self.columns.items():
            self._sheet[value + str(1)] = key
        for i in range(length + 1, length + 3):
            self._sheet.cell(row=1, column=i)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.save()

    def append_row(self, record: Requisites):
        self._sheet.append(record.get_data())

    def append_rows(self, records: List[Requisites]):
        for record in records:
            self.append_row(record)

    def save(self):
        self._workbook.save(self._path_to_save)
