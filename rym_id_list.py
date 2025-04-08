import re

import file_handler


class RymIdInMMDatabaseListManager:
    def __init__(self, path_to_json):
        self.path_to_json = path_to_json
        self.rym_ids_in_mm = file_handler.open_json(self.path_to_json)

    def add_id(self, release_to_add: dict, releases_in_mm):
        rym_id_raw: str = release_to_add["rym_id"]
        rym_id = re.findall(r'\d+', rym_id_raw)[0]
        self.rym_ids_in_mm[rym_id] = {
            "artist_name_rym": release_to_add["artist"],
            "release_title_rym": release_to_add["release_title"],
            "artist_name_mm": [rel[0] for rel in releases_in_mm],
            "release_title_mm": [rel[1] for rel in releases_in_mm],
        }

    def print_rym_ids_to_file(self):
        file_handler.save_to_json(self.rym_ids_in_mm, self.path_to_json)
