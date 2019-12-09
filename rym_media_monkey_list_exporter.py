import rym_list_parser, file_handler, com_handler, logger
import os, sys
from pathlib import Path


abspath = Path(os.path.dirname(os.path.realpath(__file__)))
source_path = 'lists'


if __name__ == "__main__":
    config = {
        "parent_list_name": "RYMtoMM",
        "exact_matches_only" : False,
        'max_entries': 0,
        'releases_per_sub_list' : 100,
    }

#    playlist_name = "2019"
    playlist_name = 'Top Albums'
#    playlist_name = "Singles 1984"
    
    list_path = abspath / source_path / playlist_name
    os.chdir(list_path)
    
    sys.stdout = logger.Logger()

    rym_list_parser = rym_list_parser.rym_list_parser(config)
    ComHandler = com_handler.ComHandler(config)
    

    parsed_list = rym_list_parser.parse_list(playlist_name)
    file_handler.save_to_yaml(parsed_list, playlist_name)
    parsed_list = file_handler.open_yaml(playlist_name)
    db_written = ComHandler.process_rym_list(parsed_list, playlist_name)
    print(f"{'List processed successfully' if db_written else 'Error: List could not be processed'}")
    ComHandler.close_com()