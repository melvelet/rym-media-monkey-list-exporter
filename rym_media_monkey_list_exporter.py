import os
from pathlib import Path

import com_handler
import file_handler
import rym_id_list
import rym_list_parser

abspath = Path(os.path.dirname(os.path.realpath(__file__)))
source_path = 'lists'

if __name__ == "__main__":
    # playlist_name = "All (A)-No-HH&M-pop3"
    playlist_name = '1992 (S)'
    # playlist_name = "IDM (AEP)"

    list_path = abspath / source_path / playlist_name
    os.chdir(list_path)

    config = {
        "parent_list_name": "RYMtoMM",
        "exact_matches_only": True,
        "max_entries": 0,
        "releases_per_sub_list": 0,
        "start_from_entry": 1,
    }

    rym_ids_in_mm_file_name = "rym_ids_in_mm.json"

    rym_id_in_mm_list_manager = rym_id_list.RymIdInMMDatabaseListManager(abspath / rym_ids_in_mm_file_name)
    rym_list_parser = rym_list_parser.RymListParser(config)
    ComHandler = com_handler.ComHandler(config, rym_id_in_mm_list_manager)

    print("Parsing RateYourMusic list...")
    parsed_list = rym_list_parser.parse_list(playlist_name)
    print("Saving RateYourMusic list to yml...")
    file_handler.save_to_yaml(parsed_list, playlist_name)
    try:
        ComHandler.open_com()
        parsed_list = file_handler.open_yaml(playlist_name)
        db_written = ComHandler.process_rym_list(parsed_list, playlist_name)
        print(f"{'List processed successfully' if db_written else 'Error: List could not be processed'}")
        rym_id_in_mm_list_manager.print_rym_ids_to_file()
        print(f"Printing list of RYM IDs found in MM database to {rym_ids_in_mm_file_name}")
    except KeyboardInterrupt:
        print("List processing aborted by user")
    finally:
        ComHandler.close_com()
