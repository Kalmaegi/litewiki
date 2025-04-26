import os
from typing import List, Dict


def read_md_files_from_dir(directory: str, max_depth: int = 1) -> List[Dict[str, str]]:
    md_files = []

    def helper(current_dir, current_depth):
        if current_depth > max_depth:
            return
        for entry in os.listdir(current_dir):
            path = os.path.join(current_dir, entry)
            if os.path.isfile(path) and entry.endswith(".md"):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    md_files.append({"path": path, "content": content})
                except Exception as e:
                    print(f"read file failed: {path}, error: {e}")
            elif os.path.isdir(path):
                helper(path, current_depth + 1)

    helper(directory, 1)
    return md_files


def aggregate_md_contents(md_files: List[Dict[str, str]]) -> str:
    """
    Aggregate md files contents into a string
    :param md_files: List[Dict]，each element contains 'path' and 'content'
    :return: str
    """
    parts = []
    for item in md_files:
        part = f"File path: {item['path']}\nContent:\n{item['content']}\n{'=' * 40}\n"
        parts.append(part)
    return "\n".join(parts)
