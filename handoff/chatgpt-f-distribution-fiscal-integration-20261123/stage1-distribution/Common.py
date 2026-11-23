"""Common validation and byte-stable CSV rendering."""
import csv
import hashlib
import io
import json
import math
from collections import Counter

class Checks:
    def __init__(self):
        self.groups = Counter()

    def __call__(self, group, actual, expected):
        same = (math.isclose(actual, expected, abs_tol=1e-7, rel_tol=2e-10)
                if isinstance(actual, float) and isinstance(expected, (int, float)) else actual == expected)
        assert same, (group, actual, expected)
        self.groups[group] += 1

    def save(self, folder):
        (folder/"Validation.json").write_text(json.dumps(
            dict(checks=sum(self.groups.values()), failures=0, groups=self.groups), indent=2)+"\n")

def render(rows):
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode()

def read_verified(path, dependency):
    data = path.read_bytes()
    assert (len(data), hashlib.sha256(data).hexdigest()) == (dependency["size"], dependency["sha256"])
    return data

def csv_rows(data):
    return list(csv.DictReader(io.StringIO(data.decode())))

def fixed_f(path, dependency):
    return {int(r["year"]): r for r in csv_rows(read_verified(path, dependency)) if r["case"] == "LEGACY_F"}
