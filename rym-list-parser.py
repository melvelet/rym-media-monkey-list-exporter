from os import path
from bs4 import BeautifulSoup

abspath = path.abspath(__file__)
listpath = 'lists/'

def _open_html(list_name, file_no):
    file_path = path.join(listpath, list_name, f"{file_no}.htm")
    with open(file_path, 'r') as stream:
        try:
            soup = BeautifulSoup(stream, features="html.parser")
        except (IOError) as exc:
            print(exc)
    return soup

def _parse_page(page):
    table = page.find(class_='mbgen')
    for i in range(len(list(table.children)) // 3):
        entry_source = list(table.children)[3 * i + 1]
        entry = _parse_entry(entry_source)
        print(entry)

def _parse_entry(entry_source):
    entry = {
        'entry_no': int(entry_source.find(class_='ooookiig').string),
        'artist': entry_source.find(class_='artist').string,
        'album': entry_source.find(class_='album').string
    }
    return entry

def parse_list(list_name):
    page_no = 0
    page = _open_html(list_name, page_no + 1)
    _parse_page(page)

if __name__ == "__main__":
    parse_list('2019')