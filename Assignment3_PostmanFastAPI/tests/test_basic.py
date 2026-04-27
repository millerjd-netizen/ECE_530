from pathlib import Path


def test_assignment3_file_exists():
    assert Path("Postman_APIS_in_class").exists()


def test_assignment3_file_not_empty():
    assert Path("Postman_APIS_in_class").stat().st_size > 0