import sqlite3
import file_handler, com_handler
from pathlib import Path
import win32com.client

def cmp(a, b):
    return (a > b) - (a < b) 


class mm_database_editor(object):
    def __init__(self, config):
        # self.MM_PATH = "/media/melvelet/Volume1/MM/MM.DB"
#        self.MM_PATH = "/home/melvelet/PlayOnLinux's virtual drives/MediaMonkey/drive_c/users/melvelet/Application Data/MediaMonkey/MM.DB"
        self.MM_PATH = Path("C:/Users/Melwin/AppData/Roaming/MediaMonkey/MM.DB")
        self.conn = self.__connect_to_db()
        self.c = self.conn.cursor()
        # self.c.execute("SELECT load_extension('SQLite3MM.dll');")
        self.id_field = config["id_field"]
        self.parent_list_name = config["parent_list_name"]
        self.parent_list_id = self.__get_parent_playlist()
        self.com_handler = com_handler.ComHandler(self.id_field)


    def __connect_to_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.MM_PATH)
        except sqlite3.Error as e:
            print(e)
        conn.create_collation('IUNICODE', self.__iUnicodeCollate)
        return conn


    def commit_and_close(self):
        self.conn.commit()
        self.conn.close()


    def __iUnicodeCollate(self, s1, s2):
        length = max(len(s1), len(s2))
        return cmp(s1.lower().zfill(length), s2.lower().zfill(length))


    def __get_songs_from_album_string(self, artist, album):
        songs = self.__get_songs_from_album_string_exact_match(artist, album)

        # if not songs:
        #     songs = self.__get_songs_from_album_string_as_substring(artist, album)

        return songs


    def __get_songs_from_album_string_exact_match(self, artist, album):
        self.c.execute("SELECT ID, Artist, SongTitle FROM main.Songs WHERE Artist LIKE ? AND Album LIKE ? \
            ORDER BY DiscNumber, TrackNumber;", [artist, album])
        return self.c.fetchall()


    def __get_songs_from_album_string_as_substring(self, artist, album):
        self.c.execute("SELECT ID, Artist, SongTitle FROM main.Songs WHERE CHARINDEX(?, Artist) > 0 AND CHARINDEX(?, Album) > 0 \
            ORDER BY DiscNumber, TrackNumber;", [artist, album])
        return self.c.fetchall()


    def __get_songs_from_rym_id(self, rym_id):
        self.c.execute(f"SELECT ID, Artist, SongTitle FROM main.Songs WHERE {self.id_field} COLLATE NOCASE LIKE ? \
            ORDER BY DiscNumber, TrackNumber;", [rym_id])
        return self.c.fetchall()


    def __write_rym_to_db(self, songs, rym_id):
        ids = self.__get_mm_ids(songs)
        self.c.executemany(f"UPDATE main.Songs SET {self.id_field} = ? WHERE _rowid_ = ?",
            [(rym_id, id_[0]) for id_ in ids])
#        self.com_handler.write_rym_to_db(ids, rym_id)


    def __get_mm_ids(self, songs):
        return [[song[0]] for _, song in enumerate(songs)]


    def __process_album(self, artist, album, rym_id):
        found_via = ''
        songs = self.__get_songs_from_rym_id(rym_id)        
        if songs:
            found_via = 'id'
        else:
            songs = self.__get_songs_from_album_string(artist, album)
            if songs:
                self.__write_rym_to_db(songs, rym_id)
                found_via = 'name'
                
        self.com_handler.write_rym_to_db(self.__get_mm_ids(songs), rym_id)

        return found_via, songs


    def __get_parent_playlist(self):
        self.parent_list_id = 0
        return self.__get_playlist_id_from_name(self.parent_list_name)


    def __get_playlist_id_from_name(self, playlist_name):
        self.c.execute("SELECT IDPlaylist FROM main.Playlists WHERE PlaylistName LIKE ?;",
            [playlist_name])
        playlist_id = self.c.fetchall()

        if not playlist_id:
            self.__create_new_playlist(playlist_name, self.parent_list_id)
            return self.__get_playlist_id_from_name(playlist_name)

        return playlist_id[0][0]


    def __create_new_playlist(self, playlist_name, parent_playlist_id):
        self.c.execute(f"INSERT INTO main.Playlists (PlaylistName,ParentPlaylist) VALUES (?,?);",
            [playlist_name, parent_playlist_id])


    def __clean_playlist(self, playlist_id):
        self.c.execute(f"SELECT _rowid_ FROM main.PlaylistSongs WHERE IDPlaylist = ?;", [playlist_id])
        ids = self.c.fetchall()
        if ids:
            self.c.executemany(f"DELETE FROM main.PlaylistSongs WHERE _rowid_ = ?;", [id_ for id_ in ids])


    def __insert_songs_into_mm_playlist(self, playlist_id, songs):
        self.__clean_playlist(playlist_id)
        ids = [id_[0] for id_ in songs]
        self.c.executemany("INSERT INTO main.PlaylistSongs(IDPlaylist,IDSong,SongOrder) VALUES (?,?,?);",
            [(playlist_id, id_, i+1) for i, id_ in enumerate(ids)])


    def __get_songs_from_rym_playlist(self, rym_playlist):
        playlist_songs = []
        stats = {'found': 0, 'notfound': 0}
        for entry_no, entry in rym_playlist.items():
            found_via, album_songs = self.__process_album(entry['artist'], entry['release_title'], entry['rym_id'])
            if album_songs:
                playlist_songs += album_songs
                print(f"Found: {entry_no}. {entry['artist']} - {entry['release_title']} (found via {found_via})")
                stats['found'] += 1
            else:
                print(f"Not found: {entry_no}. {entry['artist']} - {entry['release_title']}")
                stats['notfound'] += 1

        print(f"Found: {stats['found']}, not found: {stats['notfound']}")
        return playlist_songs


    def process_rym_list(self, rym_playlist, playlist_name):
        songs = self.__get_songs_from_rym_playlist(rym_playlist)
        playlist_name = f"rym-{playlist_name}"
        playlist_id = self.__get_playlist_id_from_name(playlist_name)

        if not playlist_id or not songs:
            return False

        self.__insert_songs_into_mm_playlist(playlist_id, songs)
        return True


if __name__ == "__main__":
    mmde = mm_database_editor()
    print(mmde.SDB)
    # artist = "Depeche Mode"
    # album = "Violator"
    # rym_id = "Album12346"
    playlist_name = "2019"
    playlist_name = f"{playlist_name}_new"
    # mmde.process_rym_list(artist, album, rym_id, playlist)
    # # print(mmde.get_playlist_id_from_name(playlist))
    mmde.create_new_playlist(playlist_name)
    mmde.commit_and_close()
