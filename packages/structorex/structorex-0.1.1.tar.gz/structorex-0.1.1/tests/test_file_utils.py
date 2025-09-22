import os
import tempfile as tf

from app.file_utils import FileUtils


def test_get_file_type_description():
    t_map = {".txt": " [text]"}
    assert FileUtils.get_file_type_desc("file.txt", t_map) == " [text]"
    assert FileUtils.get_file_type_desc("file.unknown", t_map) == ""


def test_read_file_content_text():
    enc = "utf-8"
    with tf.NamedTemporaryFile(mode="w", delete=False, encoding=enc) as tmp:
        tmp.write("Hello")
        tmp_path = tmp.name
    try:
        content = FileUtils.read_file_content(tmp_path)
        assert content == "Hello"
    finally:
        os.remove(tmp_path)
