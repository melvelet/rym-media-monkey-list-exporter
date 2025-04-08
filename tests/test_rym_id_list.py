import pytest
from rym_id_list import RymIdInMMDatabaseListManager


@pytest.fixture
def releases():
    return {
        "1": {
            "artist": "Kendrick Lamar",
            "release_title": "To Pimp a Butterfly",
            "rym_id": "[Album6286502]",
        },
        "2": {
            "artist": "Kanye West",
            "release_title": "My Beautiful Dark Twisted Fantasy",
            "rym_id": "[Album3050748]",
        },
        "3": {
            "artist": "Kendrick Lamar",
            "release_title": "good kid, m.A.A.d city",
            "rym_id": "[Album3597082]",
        }
    }


def test_add_id(releases):
    sut = RymIdInMMDatabaseListManager("")

    expected_result = {
        "6286502": {
            "release_title_rym": "To Pimp a Butterfly",
            "artist_name_rym": "Kendrick Lamar",
            "release_title_mm": ["To Pimp a Butterfly"],
            "artist_name_mm": ["Kendrick Lamar"]
        },
        "3050748": {
            "release_title_rym": "My Beautiful Dark Twisted Fantasy",
            "artist_name_rym": "Kanye West",
            "release_title_mm": ["My Beautiful Dark Twisted Fantasy"],
            "artist_name_mm": ["Kanye West"]
        },
        "3597082": {
            "release_title_rym": "good kid, m.A.A.d city",
            "artist_name_rym": "Kendrick Lamar",
            "release_title_mm": ["good kid mAAd city"],
            "artist_name_mm": ["Kendrick Lamar"]
        },
    }

    sut.add_id(releases["1"], {("Kendrick Lamar", "To Pimp a Butterfly")})
    sut.add_id(releases["2"], {("Kanye West", "My Beautiful Dark Twisted Fantasy")})
    sut.add_id(releases["3"], {("Kendrick Lamar", "good kid mAAd city")})
    sut.add_id(releases["1"], {("Kendrick Lamar", "To Pimp a Butterfly")})

    assert sut.rym_ids_in_mm == expected_result
