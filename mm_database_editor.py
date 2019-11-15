import sqlite3


class mm_database_editor(object):
    def __init__(self, id_field="OrigYear"):
        # self.MM_PATH = "/media/melvelet/Volume1/MM/MM.DB"
        self.MM_PATH = "/home/melvelet/PlayOnLinux's virtual drives/MediaMonkey/drive_c/users/melvelet/Application Data/MediaMonkey/MM.DB"
        self.conn = self.__connect_to_db()
        self.c = self.conn.cursor()
        self.id_field = id_field


    def __connect_to_db(self):
        conn = None
        try:
            conn = sqlite3.connect(self.MM_PATH)
        except Error as e:
            print(e)
        return conn


    def commit_and_close(self):
        self.conn.commit()
        self.conn.close()


    def __get_songs_from_album_string(self, artist, album):
        self.c.execute("SELECT ID, SongTitle FROM main.Songs WHERE Artist LIKE ? \
            AND Album LIKE ? ORDER BY _rowid_ ASC LIMIT 0, 50000;", [artist, album])
        return self.c.fetchall()


    def __get_songs_from_rym_id(self, rym_id):
        self.c.execute(f"SELECT ID, SongTitle FROM main.Songs WHERE {self.id_field} LIKE ?;", [rym_id])
        return self.c.fetchall()


    def __write_rym_to_db(self, songs, rym_id):
        ids = self.__get_mm_ids(songs)
        [(self.id_field, rym_id, id_[0]) for id_ in ids]
        self.c.executemany(f"UPDATE main.Songs SET {self.id_field} = ? WHERE _rowid_ = ?",
            [(rym_id, id_[0]) for id_ in ids])


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

        return found_via, songs


    def __get_playlist_id_from_name(self, playlist_name):
        self.c.execute("SELECT IDPlaylist FROM main.Playlists WHERE PlaylistName LIKE ?;",
            [playlist_name])
        playlist_id = self.c.fetchall()

        if not playlist_id:
            self.__create_new_playlist(playlist_name)
            return self.__get_playlist_id_from_name(playlist_name)

        return playlist_id[0][0]


    def __create_new_playlist(self, playlist_name):
        self.c.execute(f"INSERT INTO main.Playlists (PlaylistName,ParentPlaylist) VALUES (?,0);",
            [playlist_name])


    def __clean_playlist(self, playlist_id):
        self.c.execute(f"SELECT _rowid_ FROM main.PlaylistSongs WHERE IDPlaylist = ?;", [playlist_id])
        ids = self.c.fetchall()
        if ids:
            # self.c.execute(f"DELETE FROM main.Playlists WHERE _rowid_ = ?;", [ids[0][0]])
            self.c.executemany(f"DELETE FROM main.PlaylistSongs WHERE _rowid_ = ?;", [id_ for id_ in ids])


    def __insert_songs_into_mm_playlist(self, playlist_id, songs):
        self.__clean_playlist(playlist_id)
        ids = [id_ for id_ in songs]
        self.c.executemany("INSERT INTO main.PlaylistSongs(IDPlaylist,IDSong,SongOrder) VALUES (?,?,?);",
            [(playlist_id, id_, i+1) for i, id_ in enumerate(ids)])


    def __get_songs_from_playlist(self, rym_playlist):
        playlist_songs = {}
        stats = {'found': 0, 'notfound': 0}
        for entry_no, entry in rym_playlist.items():
            found_via, album_songs = self.__process_album(entry['artist'], entry['release_title'], entry['rym_id'])
            if album_songs:
                playlist_songs.update(album_songs)
                print(f"Found: {entry_no}. {entry['artist']} - {entry['release_title']} (found via {found_via})")
                stats['found'] += 1
            else:
                print(f"Not found: {entry_no}. {entry['artist']} - {entry['release_title']}")
                stats['notfound'] += 1

        print(f"Found: {stats['found']}, not found: {stats['notfound']}")
        return playlist_songs


    def process_rym_list(self, rym_playlist, playlist_name):
        songs = self.__get_songs_from_playlist(rym_playlist)
        playlist_name = f"rym-{playlist_name}"
        playlist_id = self.__get_playlist_id_from_name(playlist_name)

        if not playlist_id or not songs:
            return False

        self.__insert_songs_into_mm_playlist(playlist_id, songs)
        return True


if __name__ == "__main__":
    mmde = mm_database_editor()
    # artist = "Depeche Mode"
    # album = "Violator"
    # rym_id = "Album12346"
    playlist_name = "2019"
    playlist_name = f"{playlist_name}_new"
    # mmde.process_rym_list(artist, album, rym_id, playlist)
    # # print(mmde.get_playlist_id_from_name(playlist))
    mmde.create_new_playlist(playlist_name)
    mmde.commit_and_close()
