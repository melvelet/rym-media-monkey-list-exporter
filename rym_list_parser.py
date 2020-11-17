import os, glob
from bs4 import BeautifulSoup
import file_handler
from pathlib import Path


class rym_list_parser(object):
    def __init__(self, config):
        self.config = config


    def parse_list(self, list_name):
        print("Parsing RateYourMusic list...")
        parsed_list = {}
        for file in glob.glob("*.html"):
            page = file_handler.open_html(file)
            parsed_page = self.__parse_page(page)
            parsed_list.update(parsed_page)

        return self.__add_leading_zeroes(parsed_list)


    def __parse_page(self, page):
        # table = page.find(class_='ooookiig').parent.parent.parent # top list
        table = page.find(class_='charts_page') #custom charts
        parsed_page = {}
        entries = [entry_source for i, entry_source in enumerate(list(table.children)) if i > 4 and i % 2 != 0]

        for entry_source in entries:
            entry = self.__parse_entry(entry_source)
            if not entry:
                break
            parsed_page.update(entry)

        return parsed_page


    def __parse_entry(self, entry_source):
        max_entries = self.config['max_entries']        
        entry_no = self.__get_entry_no(entry_source)

        if max_entries and int(entry_no) > max_entries:
            return None

        return {
            entry_no : {
                'artist' : self.__get_artist(entry_source),
                'artist_from_link' : self.__get_artist_from_link(entry_source),
                'release_link' : self.__get_release_link(entry_source),
                'release_title' : self.__get_release_title(entry_source),
                'release_type' : self.__get_release_type(entry_source),
                'rym_id' : self.__get_rym_id(entry_source),
                'primary_genres' : self.__get_primary_genres(entry_source),
                'secondary_genres' : self.__get_secondary_genres(entry_source),
                'descriptors' : self.__get_descriptors(entry_source),
            }
        }


    def __get_release_title(self, entry_source):
        return self.__format_attribute(entry_source.find(class_='release').string)
    
    
    def __get_release_link(self, entry_source):
        return f"https://rateyourmusic.com{self.__format_attribute(entry_source.find(class_='release')['href'])}"
    
    
    def __get_release_type(self, entry_source):
        return self.__get_release_link(entry_source).split('/')[4]


    def __get_artist(self, entry_source):
        if len(entry_source.find_all(class_='artist')) > 1:
            return self.__get_collab_artists(entry_source.find_all(class_='artist'))
        else:
            artist = entry_source.find(class_='artist')
            if artist.string:
                return self.__format_attribute(artist.string)
            else:
                return [self.__format_attribute(i) for i in artist.stripped_strings]
        
        
    def __get_artist_from_link(self, entry_source):
        if len(entry_source.find_all(class_='artist')) > 1:
            return ''
        else:
            artist = entry_source.find(class_='artist')['href'].split('/')[2]
            artist = artist.replace('-', ' ').replace('_', ' ')
            return self.__format_attribute(artist)


    def __get_collab_artists(self, collab_artists):
        artist = [self.__format_attribute(i) for artist in collab_artists for i in artist.stripped_strings]
        return artist

    
    def __get_rym_id(self, entry_source):
        return self.__format_attribute(entry_source.find(class_='release')['title'], remove_parenthesis=False)


    def __get_entry_no(self, entry_source):
        pos = list(entry_source.find(class_='topcharts_position').stripped_strings)[0]
        return self.__format_attribute(pos)
    
    
    def __get_multi_attribute_from_container(self, entry_source, attribute):
        genres = list(entry_source.find(class_=f"topcharts_item_{attribute}_container").stripped_strings)
        return [self.__format_attribute(genre) for genre in genres if genre != ',']
    
    
    def __get_primary_genres(self, entry_source):
        return self.__get_multi_attribute_from_container(entry_source, 'genres')


    def __get_secondary_genres(self, entry_source):
        return self.__get_multi_attribute_from_container(entry_source, 'secondarygenres')
    
    
    def __get_descriptors(self, entry_source):
        return self.__get_multi_attribute_from_container(entry_source, 'descriptors')
    

    def __format_attribute(self, attribute, remove_parenthesis=True):
        if attribute.endswith(','):
            attribute = attribute[0:-1]
        if remove_parenthesis and attribute.startswith('[') and attribute.endswith(']'):
            attribute = attribute[1:-1]
        return f"{attribute}"


    def __get_config(self, max_entries):
        return {
            'max_entries' : max_entries,
        }
        

    def __add_leading_zeroes(self, my_dict):
        decimals = len(f"{len(my_dict)}")
        new_dict = {}
        for entry_no, entry in my_dict.items():
            new_dict.update({entry_no.zfill(decimals) : entry})
        return new_dict


if __name__ == "__main__":
    config = {
        'max_entries': 100
    }    
    playlist_name = '1984 (A)'
    
    abspath = Path(os.path.dirname(os.path.realpath(__file__)))
    source_path = 'lists'
    list_path = abspath / source_path / playlist_name
    os.chdir(list_path)
    
    rym_list_parser = rym_list_parser(config)
    parsed_list = rym_list_parser.parse_list(playlist_name)
    file_handler.save_to_yaml(parsed_list, playlist_name)