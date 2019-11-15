import rym_list_parser, mm_database_editor, file_handler


if __name__ == "__main__":
    playlist_name = '2019'

    rym_list_parser = rym_list_parser.rym_list_parser()
    mm_database_editor = mm_database_editor.mm_database_editor()

    parsed_list = rym_list_parser.parse_list(playlist_name, 12)
    file_handler.save_to_yaml(parsed_list, playlist_name)
    db_written = mm_database_editor.process_rym_list(parsed_list, playlist_name)
    mm_database_editor.commit_and_close()
    print(db_written)