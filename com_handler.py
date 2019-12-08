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
        found_by = ''
        songs = self.__get_songs_by_rym_id(rym_id)
        
        if songs.Count > 1:
            found_by = 'id'
        else:
            songs, found_by = self.__find_and_get_songs_from_release_and_write_rym_id(release)
        
        return songs, found_by
    
    
    def __find_and_get_songs_from_release_and_write_rym_id(self, release):
        if release['release_type'] == 'single':
            songs, partial_match = self.__get_single_song_by_string(release)
            if songs.Count and partial_match:
                partial_match = f"{songs[0].Artist.Name} - {songs[0].Title}"
        else:
            songs, partial_match = self.__get_all_songs_by_string(release)
            if songs.Count and partial_match:
                partial_match = f"{songs[0].Artist.Name} - {songs[0].Album.Name}"
                
        if songs:
            self.__write_rym_to_db(songs, release)
        found_by = F"name{' ' + partial_match if isinstance(partial_match, str) else ''}"
        
        return songs, found_by
        
        
    def __get_songs_by_rym_id(self, rym_id):
        songs = self.db.QuerySongs(f"Songs.Comment LIKE '%{rym_id}%'")
        return self.__convert_to_song_list(self.__order_songs(songs))
    
    
    def __get_single_song_by_string(self, release):
        artist = release['artist']
        release_title = release['release_title']
        artist_from_link = release['artist_from_link']
        song_title = release_title.split(" / ")[0]
        partial_match = None
        songs = self.db.QuerySongs(f"Songs.Artist LIKE '{self.__escape_string(artist)}' AND Songs.SongTitle LIKE '{self.__escape_string(song_title)}'")

        if songs.EOF and self.config['partial_match']:
            partial_match = True
            if artist.lower() != artist_from_link:
                songs = self.db.QuerySongs(f"Songs.Artist LIKE '%{self.__escape_string(artist_from_link)}%' AND Songs.SongTitle LIKE '%{self.__escape_string(song_title)}%'")
            if songs.EOF:
                songs = self.db.QuerySongs(f"Songs.Artist LIKE '%{self.__escape_string(artist)}%' AND Songs.SongTitle LIKE '%{self.__escape_string(song_title)}%'")
       
        return self.__convert_to_song_list(self.__order_songs(songs)), partial_match
        
    
    def __get_all_songs_by_string(self, release):
        artist = release['artist']
        release_title = release['release_title']
        artist_from_link = release['artist_from_link']
        partial_match = None
        songs = self.db.QuerySongs(f"Songs.Artist LIKE '{self.__escape_string(artist)}' AND Songs.Album LIKE '{self.__escape_string(release_title)}'")

        if songs.EOF and self.config['partial_match']:
            partial_match = True
            if artist.lower() != artist_from_link:
                songs = self.db.QuerySongs(f"Songs.Artist LIKE '%{self.__escape_string(artist_from_link)}%' AND Songs.Album LIKE '%{self.__escape_string(release_title)}%'")
            if songs.EOF:
                songs = self.db.QuerySongs(f"Songs.Artist LIKE '%{self.__escape_string(artist)}%' AND Songs.Album LIKE '%{self.__escape_string(release_title)}%'")
       
        return self.__convert_to_song_list(self.__order_songs(songs)), partial_match
        
        
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
        
        
    def __build_array_string(self, elements):
        return f"({','.join([self.__escape_string(str(x)) for x in elements])})"

    
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
    
    songs, found_by = ComHandler.get_songs_from_release(release)
#    ComHandler.print_song_list(songs)
    songs = None
    print(f"found by {found_by}")
    
#    print(ComHandler.escape_string("Let's Dance"))
    
#    songs = ComHandler.get_songs_by_string(artist, album)
#    ComHandler.print_songs(songs)
#    songs = None
#    
#    songs = ComHandler.get_songs_by_rym_id(rym_id)
#    ComHandler.print_songs(songs)
#    songs = None
        
#    ComHandler.write_rym_to_db(songs, 1)