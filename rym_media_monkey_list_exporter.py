import rym_list_parser, mm_database_editor, file_handler, com_handler
import os
from pathlib import Path


abspath = Path(os.path.dirname(os.path.realpath(__file__)))
source_path = 'lists'


if __name__ == "__main__":
    config = {
        "parent_list_name": "RYMtoMM",
        "exact_matches_only" : False,
        'max_entries': 0
    }

#    playlist_name = "2019"
#    playlist_name = 'Top Albums'
    playlist_name = "Singles 1984"
    
    list_path = abspath / source_path / playlist_name
    os.chdir(list_path)

    rym_list_parser = rym_list_parser.rym_list_parser(config)
#    mm_database_editor = mm_database_editor.mm_database_editor(config)
    ComHandler = com_handler.ComHandler(config)
    

    parsed_list = rym_list_parser.parse_list(playlist_name)
    file_handler.save_to_yaml(parsed_list, playlist_name)
#    parsed_list = file_handler.open_yaml(playlist_name)
    db_written = ComHandler.process_rym_list(parsed_list, playlist_name)
#    db_written = mm_database_editor.process_rym_list(parsed_list, playlist_name)
#    mm_database_editor.commit_and_close()
    print(f"{'List processed successfully' if db_written else 'Error: List could not be processed'}")
    ComHandler.close_com()