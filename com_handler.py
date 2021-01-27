import win32com.client
import re

from typing import Set

from logger import Logger


def get_found_via_str(found_via_type, songs, release):
    found_releases: Set[str] = set([])
    result_str = ''
    for i in range(len(songs)):
        if release['release_type'] == 'single':
            if str.lower(release['release_title']).startswith(str.lower(songs[i].Title)) \
                    and str.lower(release['artist']) == str.lower(songs[i].Artist.Name):
                continue
            else:
                found_releases.add(f"{songs[i].Artist.Name} - {songs[i].Title}")
        else:
            if str.lower(release['release_title']) == str.lower(songs[i].Album.Name) \
                    and str.lower(release['artist']) == str.lower(songs[i].Artist.Name):
                continue
            else:
                found_releases.add(f"{songs[i].Artist.Name} - {songs[i].Album.Name}")

    if found_releases:
        result_str += f"{found_via_type} as:"
        for rel in found_releases:
            result_str += f"\n\t\t\t{rel}"
    return result_str if result_str else found_via_type


def print_songs_iterator(songs):
    print("print songs of iterator")
    while not songs.EOF:
        print(
            f"ID: {songs.Item.ID}, Artist: {songs.Item.Artist.Name}, Album: {songs.Item.Album.Name}, Track: {songs.Item.TrackOrder}, Title: {songs.Item.Title}")
        songs.next()


def print_song_list(song_list):
    print("print songs of song list")
    for i in range(song_list.Count):
        song = song_list.Item(i)
        print(
            f"ID: {song.ID}, Artist: {song.Artist.Name}, Album: {song.Album.Name}, Track: {song.TrackOrder}, Title: {song.Title}")


class ComHandler(object):
    def __init__(self, config):
        self.found_first_time = 0
        self.found = 0
        self.SDB = None
        self.db = None
        self.config = config
        self.logger = Logger()

    def open_com(self):
        self.SDB = win32com.client.Dispatch("SongsDB.SDBApplication")
        self.db = self.SDB.Database
        print("COM initialization successful")

    def close_com(self):
        self.SDB = None
        self.db = None

    def process_rym_list(self, parsed_list, playlist_name):
        playlist_name = f"rym-{playlist_name}"
        playlist = self.__get_playlist_by_name(self.__get_parent_playlist(), playlist_name)
        total_releases = len(parsed_list.items())
        releases_per_sub_list = self.config['releases_per_sub_list']
        start_from_entry = self.config['start_from_entry']
        self.found_first_time = 0
        self.found = 0

        if 0 < releases_per_sub_list < total_releases:
            sub_list_count = total_releases // releases_per_sub_list
            for i in range(sub_list_count):
                if start_from_entry > (i + 1) * releases_per_sub_list:
                    continue

                list_name_begin = str(i * releases_per_sub_list + 1).zfill(len(str(total_releases)))
                list_name_end = str((i + 1) * releases_per_sub_list).zfill(len(str(total_releases)))
                sub_playlist = self.__get_playlist_by_name(playlist,
                                                           f"{list_name_begin}-{list_name_end} ({playlist_name})")
                songs = self.__get_songs_from_rym_playlist(parsed_list, i * releases_per_sub_list + 1,
                                                           (i + 1) * releases_per_sub_list)
                self.__write_songs_to_playlist(songs, sub_playlist)
            if total_releases % releases_per_sub_list:
                list_name_begin = str(sub_list_count * releases_per_sub_list + 1).zfill(len(str(total_releases)))
                list_name_end = str(total_releases).zfill(len(str(total_releases)))
                sub_playlist = self.__get_playlist_by_name(playlist,
                                                           f"{list_name_begin}-{list_name_end} ({playlist_name})")
                songs = self.__get_songs_from_rym_playlist(parsed_list,
                                                           sub_list_count * releases_per_sub_list + 1, total_releases)
                self.__write_songs_to_playlist(songs, sub_playlist)
        else:
            songs = self.__get_songs_from_rym_playlist(parsed_list, 1, total_releases)
            self.__write_songs_to_playlist(songs, playlist)

        self.logger.log(f"Found: {self.found} ({self.found_first_time} for the first time) of {total_releases}")
        self.logger.close()

        return True

    def __get_songs_from_rym_playlist(self, parsed_list, start, end):
        songs = self.SDB.NewSongList

        for i, release in list(parsed_list.items())[start - 1: end]:
            songs_release, found_via_type = self.__get_songs_from_release(release)
            if songs_release.Count > 0:
                found_via_str = get_found_via_str(found_via_type, songs_release, release)
                self.logger.log(f"Found: {i}. {release['artist']} - {release['release_title']} | "
                                f"found via {found_via_str}")
                self.found += 1
                if found_via.startswith('name'):
                    songs_release.UpdateAll()
                    self.found_first_time += 1
                self.__merge_song_lists(songs, songs_release)
            else:
                self.logger.log(
                    f"Not found: {i}. {release['artist']} - {release['release_title']}\n\t{release['rym_id']}: "
                    f"{release['release_link']}")

        return songs

    def __write_songs_to_playlist(self, songs, playlist):
        playlist.Clear()
        playlist.AddTracks(songs)

    def __get_playlist_by_name(self, parent, name):
        return parent.CreateChildPlaylist(name)

    def __get_parent_playlist(self):
        return self.SDB.PlaylistByTitle(self.config['parent_list_name'])

    def __merge_song_lists(self, song_list, song_list_release):
        for i in range(song_list_release.Count):
            song_list.Add(song_list_release.Item(i))

    def __write_rym_to_db(self, song_list, release):
        for i in range(song_list.Count):
            if song_list.Item(i).Comment:
                song_list.Item(i).Comment += '\n'
            song_list.Item(i).Comment += f"{release['rym_id']}: {release['release_link']}"

    def __convert_to_song_list(self, songs):
        song_list = self.SDB.NewSongList
        while not songs.EOF:
            song_list.Add(songs.Item)
            songs.next()
        songs = None
        return song_list

    def __get_songs_from_release(self, release):
        rym_id = release['rym_id']
        found_via = None
        songs = self.__get_songs_by_rym_id(rym_id)

        if songs.Count:
            found_via = 'id'
        else:
            songs = self.__get_all_songs_by_string(release)

            if songs.Count:
                found_via = 'name'
                self.__write_rym_to_db(songs, release)

        return songs, found_via

    def __get_songs_by_rym_id(self, rym_id):
        songs = self.db.QuerySongs(f"Songs.Comment LIKE '%{rym_id}%'")
        return self.__order_songs(self.__convert_to_song_list(songs))

    def __get_all_songs_by_string(self, release):
        artist = release['artist']
        artist_from_link = release['artist_from_link']

        search_parameter, search_variable = self.__get_search_parameter_and_variable(release)

        if type(artist) != list:
            songs = self.db.QuerySongs(
                f"Songs.Artist LIKE '{self.__escape_string(artist)}' AND Songs.{search_parameter} "
                f"LIKE '{self.__escape_string(search_variable)}'")

            if songs.EOF and not self.config['exact_matches_only']:
                for i in range(3):
                    if i == 0:
                        songs = self.db.QuerySongs(
                            f"Songs.Artist LIKE '%{self.__escape_string(artist)}%' AND Songs.{search_parameter} "
                            f"LIKE '%{self.__escape_string(search_variable)}%'")
                    if i == 1:
                        if artist.lower() != artist_from_link:
                            songs = self.db.QuerySongs(
                                f"Songs.Artist LIKE '%{self.__escape_string(artist_from_link)}%' "
                                f"AND Songs.{search_parameter} LIKE '%{self.__escape_string(search_variable)}%'")
                    if i == 2:
                        temp_songs = self.__get_songs_from_split_artist_string(release)
                        if temp_songs:
                            songs = temp_songs
                            temp_songs = None
                    if not songs.EOF:
                        break
        else:
            for artist_i in artist:
                songs = self.db.QuerySongs(
                    f"Songs.Artist LIKE '%{self.__escape_string(artist_i)}%' AND Songs.{search_parameter} "
                    f"LIKE '{self.__escape_string(search_variable)}'")
                if not songs.EOF:
                    break

        return self.__order_songs(self.__convert_to_song_list(songs))

    def __get_songs_from_split_artist_string(self, release):
        songs = None
        search_parameter, search_variable = self.__get_search_parameter_and_variable(release)
        artists = self.__split_string_by_delimiters(release['artist'],
                                                    delimiters=(" / ", ";", " and ", " & ", "The ", " Group",
                                                                " Quartet", " Quintet", " Sextet"))
        artists = list(filter(None, artists))
        if len(artists) > 1:
            for j in range(len(artists)):
                songs = self.db.QuerySongs(
                    f"Songs.Artist LIKE '%{self.__escape_string(artists[j])}%' AND Songs.{search_parameter} LIKE '%{self.__escape_string(search_variable)}%'")
                if not songs.EOF:
                    break
        return songs

    def __get_search_parameter_and_variable(self, release):
        release_title = release['release_title']
        if release['release_type'] == 'single':
            search_variable = release_title.split(" / ")[0]
            search_parameter = "SongTitle"
        else:
            search_variable = release_title
            search_parameter = "Album"
        return search_parameter, search_variable

    def __get_songs_by_mm_id(self, ids):
        id_string = self.__build_array_string(ids)
        return self.db.QuerySongs(f"Songs.ID IN {id_string}")

    def __order_songs(self, songs):
        song_list = []
        for i in range(songs.Count):
            song_list.append((songs.Item(i).DiscNumber, songs.Item(i).TrackOrder, i))

        song_list.sort()
        ordered_ids = [v[2] for _, v in enumerate(song_list)]

        for i in range(len(ordered_ids)):
            songs.Add(songs.Item(ordered_ids[i]))

        for i in range(len(ordered_ids)):
            songs.Delete(0)

        return songs

    def __escape_string(self, my_string):
        return my_string.replace("'", "''")

    def __build_array_string(self, elements):
        return f"({','.join([self.__escape_string(str(x)) for x in elements])})"

    def __split_string_by_delimiters(self, my_string, delimiters):
        regexPattern = '|'.join(map(re.escape, delimiters))
        return re.split(regexPattern, my_string)


if __name__ == "__main__":
    config = {
        "parent_list_name": "RYMtoMM",
        "partial_match": True,
    }

    release = {
        'artist': 'Depeche Mode',
        'release_title': 'Previously Unreleased Rehearsal Recordings',
        'rym_id': '[Album0]'
    }

    playlist_name = "2019"
    ComHandler = ComHandler(config)
    artist = "Depeche Mode"
    album = "Violator"
    rym_id = "[Album996]"

    songs, found_via = ComHandler.get_songs_from_release(release)
    #    ComHandler.print_song_list(songs)
    songs = None
    print(f"found by {found_via}")

#    print(ComHandler.escape_string("Let's Dance"))

#    songs = ComHandler.get_songs_by_string(artist, album)
#    ComHandler.print_songs(songs)
#    songs = None
#    
#    songs = ComHandler.get_songs_by_rym_id(rym_id)
#    ComHandler.print_songs(songs)
#    songs = None

#    ComHandler.write_rym_to_db(songs, 1)
