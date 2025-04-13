import main
import os
import pytest

@pytest.fixture
def test_file(tmp_path):
    file_path = 'stats/new_file.tsv'
    metadata = [{'Column Name':'File', 'Description':'The name of the file','Example':'test1in.pdf'},
                {'Column Name':'Location', 'Description':'The location of the token redacted file','Example':'1'},
                {'Column Name':'Token', 'Description':'The token redacted','Example':'Kent Jeffrey'},
                {'Column Name':'Length', 'Description':'The length of the token redacted','Example':'11'},
                {'Column Name':'Type', 'Description':'The type of token redacted','Example':'Name'},

    ]
    with open(file_path, "w") as f:
        for row in metadata:
            cell_values = row.values()
            line = "\t".join(cell_values) + '\n'
            f.write(line)

    yield file_path
    os.remove(file_path)

def test_read_file(test_file):
    with open(test_file, "r") as f:
        content = f.read()
    assert content == "File\tThe name of the file\ttest1in.pdf\nLocation\tThe location of the token redacted file\t1\nToken\tThe token redacted\tKent Jeffrey\nLength\tThe length of the token redacted\t11\nType\tThe type of token redacted\tName\n"