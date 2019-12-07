import win32com.client

class ComHandler(object):
    def __init__(self, config):
        self.SDB = win32com.client.Dispatch("SongsDB.SDBApplication")
#        pl = self.SDB.PlaylistByTitle("rym-2019")
        self.db = self.SDB.Database
        self.config = config
        # dbit = db.OpenSQL("SELECT * FROM Songs WHERE id > 0")
#        songs = self.db.QuerySongs("Songs.Album = 'Violator'")
#        print(songs)
#        song = songs.Item
#        print(song.AlbumName)
        
        #    player.clear()
        #    print(player.title)
        print("COM initialization successful")
        
        
    def print_songs_iterator(self, songs):
        print("print songs of iterator")
        while not songs.EOF:
            print(f"ID: {songs.Item.ID}, Artist: {songs.Item.Artist.Name}, Album: {songs.Item.Album.Name}, Track: {songs.Item.TrackOrder}, Title: {songs.Item.Title}")
            songs.next()
            
            
    def print_song_list(self, song_list):
        print("print songs of song list")
        for i in range(song_list.Count - 1):
            song = song_list.Item(i).Lyricist
            print(f"ID: {song.ID}, Artist: {song.Artist.Name}, Album: {song.Album.Name}, Track: {song.TrackOrder}, Title: {song.Title}")
            songs.next()
            
        
    def process_rym_list(self, parsed_list, playlist_name):
        playlist_name = f"rym-{playlist_name}"
        playlist = self.__get_playlist_from_name(playlist_name)
        
        if not playlist:
            return False
        
        for i, release in parsed_list.items():
            self.__process_release(release)
            
        return True
            
    
    def __get_playlist_by_name(self, name):
        return self.__get_parent_playlist().CreateChildPlaylist(name)
    
    
    def __get_parent_playlist(self):
        return self.SDB.PlaylistByTitle(self.config.parent_list_name)

        
    def __write_rym_to_db(self, songs, rym_id):
        song_list = self.__convert_to_song_list(songs)
        for i in range(song_list.Count - 1):
            song_list.Item(i).Lyricist = rym_id
        song_list.UpdateAll()
        return self.__get_songs_by_rym_id(rym_id)
    
    
    def __convert_to_song_list(self, songs):
        song_list = self.SDB.NewSongList
        while not songs.EOF:
            song_list.Add(songs.Item)
            songs.next()
        songs = None
        self.print_song_list(song_list)
        return song_list
        
        
    def get_songs_from_release(self, release):
        rym_id = release['rym_id']
        songs = self.__get_songs_by_rym_id(rym_id)
        self.print_songs_iterator(songs)
        
        if not songs:
            songs = self.__get_songs_by_string(release['artist'], release['release_title'])
            self.__write_rym_to_mm(songs, rym_id)
            
        if not songs:
            return False
        
        return self.__convert_to_song_list(songs)
        
        
    def __get_songs_by_rym_id(self, rym_id):
        songs = self.db.QuerySongs(f"Songs.{self.config['id_field']} LIKE '{rym_id}'")
        return self.__order_songs(songs)
        
        
    def __get_songs_by_string(self, artist, release_title):
        songs = self.db.QuerySongs(f"Songs.Artist LIKE '{artist}' AND Songs.Album LIKE '{release_title}'")
        return self.__order_songs(songs)
        
        
    def __get_songs_by_mm_id(self, ids):
        id_string = self.__build_array_string(ids)
        return self.db.QuerySongs(f"Songs.ID IN {id_string}")
    
    
    def __order_songs(self, songs):
        song_list = []
        while not songs.EOF:
            song_list.append((songs.Item.DiscNumber, songs.Item.TrackOrder, songs.Item.ID))
            songs.next()
        songs = None
        
        song_list.sort()
        ordered_ids = [v[2] for _, v in enumerate(song_list)]
        return self.__get_songs_by_mm_id(ordered_ids)           
        
        
    def __build_array_string(self, ids):
        return f"({','.join([str(x) for x in ids])})"
    
if __name__ == "__main__":
    config = {
        "id_field": "Lyricist",
        "parent_list_name": "RYMtoMM"
    }
    
    release = {
        'artist': 'Weyes Blood',
        'release_title': 'Titanic Rising',
        'rym_id': '[Album9999224]'
    }

    playlist_name = "2019"
    ComHandler = ComHandler(config)
    artist = "Depeche Mode"
    album = "Violator"
    rym_id = "[Album996]"
    
    songs = ComHandler.get_songs_from_release(release)
    ComHandler.print_song_list(songs)
    songs = None
    
#    songs = ComHandler.get_songs_by_string(artist, album)
#    ComHandler.print_songs(songs)
#    songs = None
#    
#    songs = ComHandler.get_songs_by_rym_id(rym_id)
#    ComHandler.print_songs(songs)
#    songs = None
        
#    ComHandler.write_rym_to_db(songs, 1)