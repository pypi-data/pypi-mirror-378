import json
import os
import zipfile
import requests
import time

from richtext_typst import convert as richtext_convert


def convert_from_json(data: dict, output_dir: str = None):
    __convert(data.get("collection", {}).get("documentStructure", {}), data.get(
        "documents", {}), data.get("collection", {}).get("name", ""), output_dir)


def convert_from_file(file_path: str, output_dir: str = None):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file {file_path}: {e}")
        return
    convert_from_json(data)


def convert_from_zip(zip_path: str, output_dir: str = None):
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"File not found: {zip_path}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            json_files = [f for f in zip_ref.namelist() if f.endswith(
                '.json') and "metadata.json" not in os.path.basename(f).lower()]
            if not json_files:
                print(f"No JSON files found in the ZIP archive: {zip_path}")
                return
            for json_file in json_files:
                with zip_ref.open(json_file) as file:
                    try:
                        data = json.load(file)
                        convert_from_json(data, output_dir)
                    except json.JSONDecodeError as e:
                        print(
                            f"Error decoding JSON from file {json_file} in ZIP: {e}")
    except zipfile.BadZipFile as e:
        print(f"Error reading ZIP file {zip_path}: {e}")


def convert_from_api(url, api_key: str, output_dir: str = None):
    try:
        filename = __get_collections(url, api_key)
    except Exception as e:
        raise e
    try:
        convert_from_zip(filename, output_dir)
        os.remove(filename)
    except Exception as e:
        raise e


def __convert(structure: dict, documents: dict, collection: str, output_dir: str = None):
    """
    Recursively traverse the documentStructure, building a list of documents with their final path.
    Each path starts with the collection name, and the page name is the last member of the url.
    Returns a list of dicts: [{"id": ..., "path": ..., "title": ...}, ...]
    """
    if not structure or not documents or not collection:
        return []

    result = []

    def get_page_name(url):
        # url is like '/doc/first-page-JGz8q9Ay1B', so split by '/' and take last part
        return url.strip('/').split('/')[-1] if url else None

    def walk(nodes, parent_path, output_dir=None):
        for node in nodes:
            page_name = get_page_name(node.get("url"))
            if not page_name:
                continue
            # Build the full path: collection/page1/page2/...
            current_path = os.path.join(parent_path, page_name)
            result.append({
                "id": node.get("id"),
                "path": current_path,
                "title": node.get("title"),
                "content": richtext_convert(documents.get(node.get("id"), {}).get("data", {}), "prosemirror")
            })
            children = node.get("children", [])
            if children:
                walk(children, current_path)

    walk(structure, collection, output_dir)
    for item in result:
        if output_dir:
            file_path = os.path.join(output_dir, item["path"] + ".typ")
            __create_file(file_path, item["content"])
    print(json.dumps(result, indent=2))
    return result


def __create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


def __get_collections(url: str, api_key: str):
    url = url.rstrip('/')
    file_operation_id = __request_export(url, api_key)
    print("File operation ID:", file_operation_id)
    completed = False
    while not completed:
        time.sleep(10)
        status = __check_file_operation(url, api_key, file_operation_id)
        if status == "complete":
            completed = True
        print("Current status:", status)
    result = _get_file_result(url, api_key, file_operation_id)
    print("File operation result URL:", result)
    return result


def __request_export(url: str, api_key: str):
    url = f"{url}/api/collections.export_all"
    try:
        response = __outline_request(url, api_key, data={
            "format": "json"
        })
        return response.get("data", {}).get("fileOperation", {}).get("id")
    except requests.RequestException as e:
        raise Exception("Error fetching collections from API: " + str(e))


def __check_file_operation(url: str, api_key: str, file_operation_id: str):
    url = f"{url}/api/fileOperations.info"
    try:
        response = __outline_request(url, api_key, data={
            "id": file_operation_id
        })
        return response.get("data", {}).get("state")
    except requests.RequestException as e:
        raise Exception(
            "Error checking file operation status from API: " + str(e))


def _get_file_result(url: str, api_key: str, file_operation_id: str):
    url = f"{url}/api/fileOperations.redirect"
    try:
        return __outline_request(url, api_key, data={
            "id": file_operation_id
        }, file_expected=True)
    except requests.RequestException as e:
        raise Exception(
            "Error fetching file operation result from API: " + str(e))


def __outline_request(url: str, api_key: str, data=None, file_expected: bool = False):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers,
                             json=data, stream=file_expected)
    if response.status_code == 200:
        if file_expected:
            filename = "output.zip"
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return filename
        return response.json()

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", None)
        raise Exception("Rate limit exceeded. Please try again later." +
                        (f" Retry-After: {retry_after}s" if retry_after else ""))
    raise Exception(
        f"Request failed with status code {response.status_code}: {response.text}")
