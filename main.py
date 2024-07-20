import os
import pathlib
import hashlib
import pickle
from pathlib import Path
import shutil
import re
import csv

class DuplicateDatabase:
    def __init__(self) -> None:
        self.db = {} #type: dict[str, list[str]]

    def add(self, path, sha256):
        if sha256 not in self.db:
            self.db[sha256] = []

        self.db[sha256].append(path)

scan_folder = 'input'
output_dir = 'output'
out_csv_path = 'bgm-to-sha.csv'

def sha256sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def caculate_sha256_of_files_in_folder(folder, relative_folder):
    if not os.path.exists(folder):
        print(f"ERROR: input folder '{folder}' missing!")
        exit(-1)
    

    shas = []

    # iterate through all original hou sprites and calculate their SHA256
    for path in pathlib.Path(folder).rglob('*.ogg'):
        sha256 = sha256sum(path)
        relpath = path.relative_to(relative_folder)

        print(f'{relpath} -> {sha256}')

        shas.append((relpath, sha256))

    return shas


# Record all paths in 'input' folder
path_checklist = {}
for path in pathlib.Path(scan_folder).rglob('*.ogg'):
    relpath = path.relative_to(scan_folder)
    path_checklist[relpath] = None
num_ogg = len(path_checklist)

# Scan folders in the order specified below
database = DuplicateDatabase()

folders_to_scan = [
    'question/BGM',
    'question/OGBGM',
    'question/HouPlusBGM',
    'question/HouPlusDemoBGM',
    'question/RemakeBGM',
]

for folder in folders_to_scan:
    sha_path_tuples = caculate_sha256_of_files_in_folder(Path(scan_folder).joinpath(folder), scan_folder)
    for (path, sha) in sha_path_tuples:
        path_checklist.pop(path)
        database.add(str(path), sha)

# Check all paths were covered
num_not_covered = len(path_checklist)
if num_not_covered > 0:
    print(f"Error: {num_not_covered} paths not covered:")
    for (path, _) in path_checklist.items():
        print(f' - NOT COVERED: {path}')
    raise Exception(f"Error: {num_not_covered} paths not covered:")
else:
    print(f"OK - all {num_ogg} files covered")

for (sha, path) in database.db.items():
    print(f'{sha} -> {path}')


# with open(out_csv_path, 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting = csv.QUOTE_ALL)
#     for path, sha256 in mapping:
#         writer.writerow([path, sha256])


# unique_mapping = {}

# dup_count = 0

# for path, sha256 in mapping:
#     if sha256 in unique_mapping:
#         dup_count += 1
#         if path not in unique_mapping[sha256]:
#             unique_mapping[sha256][path] = None
#     else:
#         unique_mapping[sha256] = {path: {None}}

# print(f"Found {dup_count} duplicates")

# for key, value in unique_mapping.items():
#     source = os.path.join(scan_folder, list(value)[0])
#     dest = os.path.join(output_dir, list(value)[0])

#     # print(f"{source} -> {dest}")
#     Path(dest).parent.mkdir(parents=True, exist_ok=True)
#     shutil.copy(source, dest)