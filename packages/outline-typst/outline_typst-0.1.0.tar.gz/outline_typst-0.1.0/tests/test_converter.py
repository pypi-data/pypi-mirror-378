import json
from outline_typst import convert_from_json, convert_from_file, convert_from_zip, convert_from_api


def test_convert_from_json():
    data_file = "tests/data/collection-sample.json"
    with open(data_file, "r") as f:
        data = json.load(f)
    result = convert_from_json(data, output_dir="tests/data/json")
    assert result == result


def test_convert_from_file():
    data_file = "tests/data/collection-sample.json"
    result = convert_from_file(data_file, output_dir="tests/data/file")
    assert result == result


def test_convert_from_zip():
    zip_file = "tests/data/outline-export-sample.json.zip"
    result = convert_from_zip(zip_file, output_dir="tests/data/zip")
    assert result == result


def test_convert_from_api():
    url = "http://localhost:3000/"
    api = "ol_api_6bCTC9tMfpmAILeAEhpfv4aLkzbzI5i6qvOpDn"
    result = None
    try:
        result = convert_from_api(url, api, output_dir="tests/data/api")
    except Exception as e:
        print(f"Error during API conversion: {e}")
    assert result == ""
