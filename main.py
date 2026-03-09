import pytesseract
from numpy.f2py.auxfuncs import replace
from pdf2image import convert_from_path
import re
import os


def ocr_title_page(path):
    title_page = convert_from_path(path,
                                   first_page=1,
                                   last_page=1
                                   )
    title_page = title_page[0]
    print(title_page)

    text = pytesseract.image_to_string(title_page,
                                       config= '-l pol'
                                       )

    return text

def find_pesel(text: str) -> str:
    match = re.findall(
        r'Nr\s*PESEL[: ]\s*\d{11}',
        text
    )

    return match

def find_numbers(text: str) -> str:
    nr = re.findall(r'NR\s*\d+\s*\/\s*20\d{2}', text)
    return nr

def get_name(pesel:str,
            card_number:str) -> str:

    if pesel is None or card_number is None:
        return False

    try:
        raw_pesel = [x.replace('Nr PESEL: ', '') for x in pesel]

        nr_card = [x.replace('NR ', '') for x in card_number]
        nr_card = nr_card[0].split('/')

        patient_number = nr_card[0]
        year = nr_card[1]

        return  'KI_WG.' + year + '^' + patient_number + '^0_P.' + raw_pesel[0] + '.pdf'

    except Exception as e:
        print(e)
        return []


def main():
    pathIn = 'in/'
    pathOutOk = 'outOk/'
    pathOutError = 'outError/'

    path = 'test.pdf'
    print(path)

    text = ocr_title_page(pathIn + path)
    # print('zeskanowana strona',text)

    pesel = find_pesel(text)
    print('PESEL:', pesel)

    nr = find_numbers(text)
    print('numer karty:', nr)

    result = get_name(pesel=pesel,
                    card_number=nr)

    if result:
        os.rename(pathIn + path, pathOutOk + result)
        print('Poprawnie zmieniono nazwę pliku na: {}'.format(result))

    else:
        os.rename(pathIn + path, pathOutError + path)
        print('Błąd przy odczycie ' + path)


if __name__ == "__main__":
    main()
