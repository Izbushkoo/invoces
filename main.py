import asyncio
import datetime
import os
from typing import Optional, List, Union

# os.system('pip install -r requirements.txt')

import PyPDF2
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from openpyxl import Workbook


from dotenv import load_dotenv


load_dotenv('.env')


class Requisites(BaseModel):
    """Identifying information about invoice in a text."""

    invoice_date: str = Field(..., description="Date of invoice from a text")
    customer_name: str = Field(..., description="Name of a company or customer")
    customer_city: str = Field(..., description="Customer's city")
    customer_street: str = Field(..., description="Customer's street")
    customer_postal_code: str = Field(..., description="Customer's postal code")
    # address_without_coutry_code: str = Field(..., description="Geschäftsadresse address from a text, without country code")
    country_code: str = Field(..., description="Customer Country code of invoice from a text")
    customer_vat_id: Optional[str] = Field(..., description="A value-added tax identification number of customer in a text")
    bestellnummer_or_contratto: str = Field(..., description="order number - a unique identifier that is "
                                                             "assigned to an order at the initial stage of the ordering process.")

    def get_data(self):
        return {
            'A': self.customer_name, 'B': self.customer_vat_id if self.customer_vat_id != "" else None,
            'C': self.customer_street, 'D': self.customer_postal_code, 'E': self.customer_city,
            'N': self.country_code, 'O': self.bestellnummer_or_contratto, 'P': self.invoice_date
        }


class WBWorker:

    columns = {
        "Name": "A", "NIP": "B", "Ulica": "C", "Kod": "D", "Miasto": "E", "email": "F", "telefon": "G",
        "Nazwa_skr": "H", "REGON": "I", "Rabat": "J", "Opis": "K", "Odbiorca": "L", "Nadawca": "M",
        "Kraj": "N"
    }

    def __init__(self, file_name: Union[str, None] = None):
        self._workbook = Workbook()
        self._sheet = self._workbook.active
        self._file_name = self._create_name() + '.xlsx' if not file_name else file_name
        self._create_title_row()

    @classmethod
    def _create_name(cls):
        return datetime.datetime.utcnow().strftime("%d_%m_%Y__%M_%S")

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
        self._workbook.save(os.path.join(os.getcwd(), self._file_name))


def get_page_1(path):
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return reader.pages[0].extract_text()


async def use_chain(input_: str):

    model = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a world class algorithm for extracting information in structured formats."),
        ("human", "Use the given format to extract information from the following text: {input}"),
        ("human", "Tip: Make sure to answer in the correct format"),
    ])
    chain = create_structured_output_chain(Requisites, model, prompt, verbose=True)
    return await chain.arun(input_)


async def main():

    # path = '/home/izbushko/Downloads/Инвойсы/drive-download-20231025T141654Z-001'
    path = os.getcwd()
    files = os.listdir(path)
    full_file_names = [os.path.join(path, file) for file in files][:2]

    tasks = []

    for file_path in full_file_names:
        text = get_page_1(file_path)

        tasks.append(
            asyncio.create_task(use_chain(text))
        )

    return await asyncio.gather(*tasks)

results = asyncio.run(main())

with WBWorker() as w:
    w.append_rows(results)

