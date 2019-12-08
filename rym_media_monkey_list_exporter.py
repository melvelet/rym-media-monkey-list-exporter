import rym_list_parser, mm_database_editor, file_handler, com_handler


if __name__ == "__main__":
    config = {
        "parent_list_name": "RYMtoMM",
        "partial_match" : True,
        'max_entries': 20
    }

    playlist_name = "2019"
#    playlist_name = 'Top Albums'

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