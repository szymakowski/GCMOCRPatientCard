import pytesseract
from pdf2image import convert_from_path
import re
import os
from pathlib import Path
from datetime import datetime, timedelta
import shutil


def ocr_title_page(path: Path) -> str:
    images = convert_from_path(path, first_page=1, last_page=1)
    text = pytesseract.image_to_string(images[0], lang="pol")
    return text


def find_pesel(text: str) -> str | None:
    match = re.search(r'Nr\s*PESEL[: ]\s*(\d{11})', text, re.IGNORECASE)
    return match.group(1) if match else None


def find_card_number(text: str) -> tuple[str, str] | None:
    match = re.search(r'NR\s*(\d+)\s*/\s*(20\d{2})', text, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return None


def build_filename(pesel: str, card: tuple[str, str]) -> str:
    patient_number, year = card
    return f"KI_WG.{year}^{patient_number}^0_P.{pesel}.pdf"


def process_file(path: Path, out_ok: Path, out_error: Path):
    try:
        text = ocr_title_page(path)
        print('caly tekst: ', text)

        pesel = find_pesel(text)
        print('PESEL PO OCR', pesel)

        card = find_card_number(text)
        print('KARTA PO OCR', card)


        if pesel and card:
            new_name = build_filename(pesel, card)
            shutil.copy2(path, out_ok / new_name)
            print(f"OK → {new_name}")
        else:
            shutil.copy2(path, out_error / path.name)
            print(f"Błąd OCR → {path.name}")

    except Exception as e:
        print("Błąd:", e)
        shutil.copy2(path, out_error / path.name)



def main():
    path_in = Path("/mnt/gcm/IT/Darek C/karty infromacyjne KCH/in")
    print(os.listdir(path_in))

    path_ok = Path("/mnt/gcm/IT/Darek C/karty infromacyjne KCH/outOk")
    path_error = Path("/mnt/gcm/IT/Darek C/karty infromacyjne KCH/outError")

    path_ok.mkdir(exist_ok=True)
    path_error.mkdir(exist_ok=True)

    for file in os.listdir(path_in):
        file_path = path_in / file
        print(file_path)

        process_file(file_path, path_ok, path_error)


if __name__ == "__main__":
    main()
