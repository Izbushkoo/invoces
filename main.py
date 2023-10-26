import asyncio
import datetime
import os
from typing import Optional, List, Union

if "requirements.txt" in os.listdir(os.getcwd()):
    os.system('pip install -r requirements.txt')

import PyPDF2
from langchain.chains.openai_functions import create_structured_output_chain
from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from openpyxl import Workbook


from dotenv import load_dotenv


load_dotenv('.env')


class Requisites(BaseModel):
    """Identifying information about invoice in a text."""

    invoice_date: str = Field(..., description="Date of invoice from a text")
    geschäftsadresse_customer_name: str = Field(..., description="geschäftsadresse Name of a company or customer")
    geschäftsadresse_city: str = Field(..., description="geschäftsadresse city")
    geschäftsadresse_street: str = Field(..., description="geschäftsadresse street")
    geschäftsadresse_state_or_land: Optional[str] = Field(..., description="geschäftsadresse state or land")
    geschäftsadresse_postal_code: str = Field(..., description="geschäftsadresse postal code")
    # address_without_coutry_code: str = Field(..., description="Geschäftsadresse address from a text, without country code")
    country_code: str = Field(..., description="Customer Country code of invoice from a text")
    customer_vat_id: Optional[str] = Field(..., description="A value-added tax identification number of customer in a text")
    bestellnummer_or_contratto: str = Field(..., description="order number - a unique identifier that is "
                                                             "assigned to an order at the initial stage of the ordering process.")

    def get_data(self):
        return {
            'A': self.geschäftsadresse_customer_name, 'B': self.customer_vat_id if self.customer_vat_id != "" else None,
            'C': self.geschäftsadresse_street, 'D': self.geschäftsadresse_postal_code,
            'E': self.geschäftsadresse_city + ', ' + self.geschäftsadresse_state_or_land \
                if self.geschäftsadresse_state_or_land else self.geschäftsadresse_city,
            'N': self.country_code, 'O': self.bestellnummer_or_contratto,
            'P': self.invoice_date
        }


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
        return datetime.datetime.utcnow().strftime("%d_%m_%Y__%H_%M")

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


def get_page_1(path):
    print(f"\nRead file {path}...OK")
    with open(path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return reader.pages[0].extract_text()


async def use_chain(input_: str, file: str):

    model = ChatOpenAI(temperature=0, model='gpt-3.5-turbo')
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a world class algorithm for extracting information in structured formats."),
        ("human", "Use the given format to extract information from the following text: {input}"),
        ("human", "Tip: Make sure to answer in the correct format and all properties encolsed in double quotes"),
    ])
    chain = create_structured_output_chain(Requisites, model, prompt)
    await asyncio.sleep(0.01)
    with get_openai_callback() as cb:
        try:
            result = await chain.arun(input_)
        except Exception:
            print(f"Error occured while getting response from openai for file {file}")
            return
        print(f"Call cost (USD) {cb.total_cost}$")

    return result


async def main():

    message = "Введите полный путь до папки с инвойсами, либо нажмите Enter для поиска в текущей папкой.\n"
    path_to_dir = str(input(message))

    while True:
        if not path_to_dir:
            path_to_dir = os.path.join(os.getcwd())
        elif not os.path.isdir(path_to_dir):
            print("Указанный путь не является папкой")
            path_to_dir = str(input(message))
            continue
        else:
            break

    # path_to_dir = '/home/izbushko/Downloads/Инвойсы/drive-download-20231025T141654Z-001'

    files = os.listdir(path_to_dir)

    if not files:
        print("Папка пуста.\n")
        return

    full_file_names = [os.path.join(path_to_dir, file) for file in files if file.endswith('.pdf')]

    if not full_file_names:
        print("В папке отстствуют PDF файлы")
        return

    tasks = []

    for file_path in full_file_names:
        text = get_page_1(file_path)

        tasks.append(
            asyncio.create_task(use_chain(text, file_path))
        )

    results = await asyncio.gather(*tasks)

    with WBWorker(path_to_save=path_to_dir) as w:
        w.append_rows(results)

    print("\nDone")


asyncio.run(main())


