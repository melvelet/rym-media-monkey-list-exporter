import win32com.client

class ComHandler(object):
    def __init__(self, config):
        self.SDB = win32com.client.Dispatch("SongsDB.SDBApplication")
        self.db = self.SDB.Database
        self.config = config
        print("COM initialization successful")
        
    
    def close_com(self):
        self.SDB = None
        self.db = None
        
        
    def print_songs_iterator(self, songs):
        print("print songs of iterator")
        while not songs.EOF:
            print(f"ID: {songs.Item.ID}, Artist: {songs.Item.Artist.Name}, Album: {songs.Item.Album.Name}, Track: {songs.Item.TrackOrder}, Title: {songs.Item.Title}")
            songs.next()
            
            
    def print_song_list(self, song_list):
        print("print songs of song list")
        for i in range(song_list.Count):
            song = song_list.Item(i)
            print(f"ID: {song.ID}, Artist: {song.Artist.Name}, Album: {song.Album.Name}, Track: {song.TrackOrder}, Title: {song.Title}")
            
        
    def process_rym_list(self, parsed_list, playlist_name):
        songs = self.__get_songs_from_rym_playlist(parsed_list)
        
        playlist_name = f"rym-{playlist_name}"
        playlist = self.__get_playlist_by_name(playlist_name)
        
        if not songs or not playlist:
            return False
        
        self.__write_songs_to_playlist(songs, playlist)
        
        return True
    
    
    def __get_songs_from_rym_playlist(self, parsed_list):
        songs = self.SDB.NewSongList
        
        for i, release in parsed_list.items():
            songs_release, found_by = self.__get_songs_from_release(release)
            if found_by:
                print(f"Found {i}. {release['artist']} - {release['release_title']} (found by {found_by})")
#                self.print_song_list(songs_release)
                self.__merge_song_lists(songs, songs_release)
            else: 
                print(f"Not found {i}. {release['artist']} - {release['release_title']}")
                
        songs.UpdateAll()
        return songs
    
    
    def __write_songs_to_playlist(self, songs, playlist):
        playlist.Clear()
        playlist.AddTracks(songs)
            
    
    def __get_playlist_by_name(self, name):
        return self.__get_parent_playlist().CreateChildPlaylist(name)
    
    
    def __get_parent_playlist(self):
        return self.SDB.PlaylistByTitle(self.config['parent_list_name'])
    
    
    def  __merge_song_lists(self, song_list, song_list_release):
        for i in range(song_list_release.Count):
            song_list.Add(song_list_release.Item(i))

        
    def __write_rym_to_db(self, song_list, rym_id):
        for i in range(song_list.Count):
            song_list.Item(i).Lyricist = rym_id
    
    
    def __convert_to_song_list(self, songs):
        song_list = self.SDB.NewSongList
        while not songs.EOF:
            song_list.Add(songs.Item)
            songs.next()
        songs = None
        return song_list
        
        
    def __get_songs_from_release(self, release):
        rym_id = release['rym_id']
        found_by = ''
        songs = self.__get_songs_by_rym_id(rym_id)
        
        if songs.Count > 1:
            found_by = 'id'
        else:
            songs = self.__get_songs_by_string(release['artist'], release['release_title'])
            self.__write_rym_to_db(songs, rym_id)
            found_by = 'name'
        
        return songs, found_by
        
        
    def __get_songs_by_rym_id(self, rym_id):
        songs = self.db.QuerySongs(f"Songs.{self.config['id_field']} LIKE '{rym_id}'")
        return self.__convert_to_song_list(self.__order_songs(songs))
        
        
    def __get_songs_by_string(self, artist, release_title):
        songs = self.db.QuerySongs(f"Songs.Artist LIKE '{self.__escape_string(artist)}' AND Songs.Album LIKE '{self.__escape_string(release_title)}'")
        return self.__convert_to_song_list(self.__order_songs(songs))
        
        
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


    def __escape_string(self, my_string):
        return my_string.replace("'","''")
        
        
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
    
#    songs, found_by = ComHandler.get_songs_from_release(release)
#    ComHandler.print_song_list(songs)
#    songs = None
#    print(f"found by {found_by}")
    
    print(ComHandler.escape_string("Let's Dance"))
    
#    songs = ComHandler.get_songs_by_string(artist, album)
#    ComHandler.print_songs(songs)
#    songs = None
#    
#    songs = ComHandler.get_songs_by_rym_id(rym_id)
#    ComHandler.print_songs(songs)
#    songs = None
        
#    ComHandler.write_rym_to_db(songs, 1)