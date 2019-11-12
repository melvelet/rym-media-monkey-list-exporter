import os, glob, re
from os import path
from bs4 import BeautifulSoup
import file_handler


abspath = os.path.dirname(os.path.realpath(__file__))
source_path = 'lists/'


def parse_list(list_name):
    list_path = path.join(source_path, list_name)
    os.chdir(list_path)

    parsed_list = {}
    for file in glob.glob("*.html"):
        page = file_handler.open_html(file)
        parsed_page = _parse_page(page)
        parsed_list.update(parsed_page)

    return parsed_list


def _parse_page(page):
    table = page.find(class_='mbgen')
    parsed_page = {}

    for i in range(len(list(table.children)) // 3):
        entry_source = list(table.children)[3 * i + 1]
        entry = _parse_entry(entry_source)
        parsed_page.update(entry)

    return parsed_page


def _parse_entry(entry_source):
    entry_no = _format_attribute(entry_source.find(class_='ooookiig').string)
    if len(entry_source.find_all(class_='artist')) > 1:
        artist = _get_collab_artists(entry_source.find_all(class_='artist'))
    else:
        artist = _format_attribute(entry_source.find(class_='artist').string)
    title = _format_attribute(entry_source.find(class_='album').string)
    rym_id = _format_attribute(entry_source.find(class_='album')['title'])

    entry = {
        entry_no : {
            'artist': artist,
            'title': title,
            'rym_id' : rym_id
        }
    }
    
    return entry


def _get_collab_artists(collab_artists):
    artist = ';'.join([artist.string if len(artist.contents) == 1
                else f"{artist.contents[0]}[{artist.contents[1].string[1:-1]}]"
                for artist in collab_artists])
    return artist


def _format_attribute(attribute):
    return f"{attribute}"


if __name__ == "__main__":
    list_name = '2019'
    parsed_list = parse_list(list_name)
    file_handler.save_to_yaml(parsed_list, list_name)