import os
from pathlib import Path

import com_handler
import file_handler
import rym_list_parser

abspath = Path(os.path.dirname(os.path.realpath(__file__)))
source_path = 'lists'

if __name__ == "__main__":
    # playlist_name = "All (A)-No-HH&M-pop3"
    playlist_name = '1992 (AEP)'
    # playlist_name = "1978 (S)"

    list_path = abspath / source_path / playlist_name
    os.chdir(list_path)

    config = {
        "parent_list_name": "RYMtoMM",
        "exact_matches_only": False,
        "max_entries": 0,
        "releases_per_sub_list": 50,
        "start_from_entry": 1,
    }

    rym_list_parser = rym_list_parser.rym_list_parser(config)
    ComHandler = com_handler.ComHandler(config)

    print("Parsing RateYourMusic list...")
    parsed_list = rym_list_parser.parse_list(playlist_name)
    print("Saving RateYourMusic list to yml...")
    file_handler.save_to_yaml(parsed_list, playlist_name)
    try:
        ComHandler.open_com()
        parsed_list = file_handler.open_yaml(playlist_name)
        db_written = ComHandler.process_rym_list(parsed_list, playlist_name)
        print(f"{'List processed successfully' if db_written else 'Error: List could not be processed'}")
    except KeyboardInterrupt:
        print("List processing aborted by user")
    finally:
        ComHandler.close_com()
