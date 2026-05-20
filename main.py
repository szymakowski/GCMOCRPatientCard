import platform
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
import re
import os
from pathlib import Path
import shutil

print('START')

def ocr_page(path: Path, page: Number) -> str:
    images = convert_from_path(path, first_page=page, last_page=page)

    # Czytanie ostatniej strony
    # info = pdfinfo_from_path(path)
    # last_page = info["Pages"]
    # images = convert_from_path(path, first_page=last_page, last_page=last_page)

    text = pytesseract.image_to_string(images[0], lang="pol")
    return text

def find_pesel_first(text: str) -> str | None:
    match = re.search(r'Nr\s*PESEL[:;\. ]\s*(\d{11})\s', text, re.IGNORECASE)
    return match.group(1) if match else None


def find_card_number_first(text: str) -> tuple[str, str] | None:
    match = re.search(r'NR\s*(\d+)\s*/\s*(20\d{2})\s', text, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return None

def find_pesel_second(text: str) -> str | None:
    match = re.search(r'Pesel[:;\. ]\s*(\d{11})\s', text, re.IGNORECASE)
    return match.group(1) if match else None


def find_card_number_second(text: str) -> tuple[str, str] | None:
    match = re.search(r'Nr\s*KG\s*(\d+)\s*/\s*(20\d{2})\s', text, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    return None


def build_filename(pesel: str, card: tuple[str, str]) -> str:
    patient_number, year = card
    return f"KI_WG.{year}^{patient_number}^0_P.{pesel}.pdf"


def save_ocr_to_file(file_path: Path, dir_path: Path, ocr_data: str):
    temp_path = os.path.join(str(dir_path), "ocr_" + os.path.basename(file_path) + ".txt")
    print(temp_path)
    with open(temp_path, "x") as text_file:
        text_file.write(ocr_data)
    # text_file.write("OCR data: {0}".format(ocr_data))
    return None


def process_file(path: Path, out_ok: Path, out_error: Path):
    try:
        print('PLIK: ', path)

        # process first page
        text = ocr_page(path, 1)

        pesel = find_pesel_first(text)
        print('PESEL PO OCR-1: ', pesel)

        card = find_card_number_first(text)
        print('KARTA PO OCR-1: ', card)

        if pesel and card:
            new_name = build_filename(pesel, card)
            shutil.copy2(path, out_ok / new_name)
            print(f"OK → {new_name}")
        else:
            print('OCR SECOND PAGE!')
            # process second page (info on top)
            text2 = ocr_page(path, 2)

            if not pesel:
                pesel = find_pesel_second(text2)
                print('PESEL PO OCR-2: ', pesel)

            if not card:
                card = find_card_number_second(text2)
                print('KARTA PO OCR-2: ', card)

            if pesel and card:
                new_name = build_filename(pesel, card)
                shutil.copy2(path, out_ok / new_name)
                print(f"OK → {new_name}")
            else:
                save_ocr_to_file(path, out_error, text + text2)
                # print('caly tekst: ', text2)
                shutil.copy2(path, out_error / path.name)
                print(f"Błąd OCR → {path.name}")

    except Exception as e:
        print("Błąd:", e)
        shutil.copy2(path, out_error / path.name)
        print(f"Błąd - przenoszę plik → {path.name}")


def count_files_in_directory(path: Path):
    return len([file for file in path.iterdir() if file.is_file()])


def main():
    # path_in = Path("/mnt/gcm/IT/KPO-digitalizacja/Praktykanci")
    # path_in = Path("/mnt/gcm/IT/KPO-digitalizacja/Praktykanci/outError")
    # print(os.listdir(path_in))

    # path_ok = Path("/mnt/gcm/IT/KPO-digitalizacja/Praktykanci/outOk")
    # path_error = Path("/mnt/gcm/IT/KPO-digitalizacja/Praktykanci/outError")

    # base_path = Path(os.getenv("BASE_DIR", "/data"))
    # base_path = Path("/data")

    if platform.system() == 'Windows':
        base_path = Path("T:/KPO-digitalizacja/Praktykanci")
    else:
        base_path = Path("/mnt/gcm/IT/KPO-digitalizacja/Praktykanci")

    path_in = base_path
    path_ok = base_path / "outOk"
    path_error = base_path / "outError"

    # print('Pliki startowe: ', count_files_in_directory(path_in))
    # print('Pliki outOk: ', count_files_in_directory(path_ok))
    # print('Pliki outError: ', count_files_in_directory(path_error))

    path_ok.mkdir(exist_ok=True)
    path_error.mkdir(exist_ok=True)

    currentIndex = 0

    for file_path in path_in.iterdir():
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() != ".pdf":
            continue

        currentIndex += 1
        print('==========================')
        print('Current index: ', currentIndex)

        # print(file_path)
        process_file(file_path, path_ok, path_error)

if __name__ == "__main__":
    main()

print('KONIEC')
