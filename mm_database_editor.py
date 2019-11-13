import sqlite3


class mm_database_editor(object):
    def __init__(self):
        self.MM_PATH = '/media/melvelet/Volume1/MM/MM.DB'
        self.conn = self.__connect_to_db()
        self.c = self.conn.cursor()


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
        # "SELECT COUNT(*) FROM (SELECT `_rowid_`,* FROM `main`.`Albums` WHERE `Album` LIKE '%Violator%' ESCAPE '\' ORDER BY `_rowid_` ASC);"
        self.c.execute("SELECT ID, SongTitle FROM main.Songs WHERE Artist LIKE ? \
            AND Album LIKE ? ORDER BY _rowid_ ASC LIMIT 0, 50000;", [artist, album])
        return self.c.fetchall()


    def __get_songs_from_rym_id(self, rym_id):
        self.c.execute("SELECT ID, SongTitle FROM main.Songs WHERE OrigYear LIKE ? \
            ORDER BY _rowid_ ASC LIMIT 0, 50000;", [rym_id])
        return self.c.fetchall()


    def __write_rym_to_db(self, songs, rym_id):
        ids = self.__get_mm_ids(songs)
        self.c.executemany("UPDATE main.Songs SET `OrigYear` = ? \
            WHERE _rowid_ = ? COLLATE IUNICODE", [(rym_id, id_[0]) for id_ in ids])


    def __get_mm_ids(self, songs):
        return [[song[0]] for _, song in enumerate(songs)]


    def process_album(self, artist, album, rym_id):
        songs = self.__get_songs_from_rym_id(rym_id)
        
        if songs:
            print("Found via ID")
        else:
            songs = self.__get_songs_from_album_string(artist, album)
            if songs:
                self.__write_rym_to_db(songs, rym_id)
                print("Found via album name")
                

        return songs


if __name__ == "__main__":
    mmde = mm_database_editor()
    artist = "Depeche Mode"
    album = "Violator"
    rym_id = "Album123456"
    mmde.process_album(artist, album, rym_id)
    mmde.commit_and_close()