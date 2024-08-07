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
    # Roughly 231 unique in question-answer
    'question/BGM',
    'question/April2019BGM',
    'question/OGBGM',
    'question/HouPlusBGM',
    'question/HouPlusDemoBGM',
    'question/RemakeBGM',
    'answer/BGM',
    'answer/ExtraBGM',
    'answer/OGBGM',
    # No unique in rei which isn't already in question/answer
    'rei/BGM',
    'rei/ExtraBGM',
    'rei/OGBGM',
    # Many hou BGM are not bit for bit identical, but are probably are actually identical?
    # This inflates the unique count from 231 -> 557
    'hou-plus/BGM',
    'hou-plus/April2019BGM',
    'hou-plus/OGBGM',
    'hou-plus/HouPlusDemoBGM',
]

for folder in folders_to_scan:
    sha_path_tuples = caculate_sha256_of_files_in_folder(Path(scan_folder).joinpath(folder), scan_folder)
    for (path, sha) in sha_path_tuples:
        path_checklist.pop(path)
        database.add(path, sha)

# Check all paths were covered
num_not_covered = len(path_checklist)
if num_not_covered > 0:
    print(f"Error: {num_not_covered} paths not covered:")
    for (path, _) in path_checklist.items():
        print(f' - NOT COVERED: {path}')
    raise Exception(f"Error: {num_not_covered} paths not covered: ({len(database.db)} unique)")
else:
    print(f"OK - all {num_ogg} files covered ({len(database.db)} unique)")

# Save the duplicate database as a python .pickle file
with open(os.path.join(output_dir, 'database.pickle'), 'wb') as f:
    pickle.dump(database.db, f)

# Copy only unique files, and information about each file
for (sha, paths) in database.db.items():
    for i, path in enumerate(paths):
        src = Path(scan_folder).joinpath(path)
        dst = Path(output_dir).joinpath(path)
        os.makedirs(dst.parent, exist_ok=True)

        # First path is the "original", need to copy
        if i == 0:
            print(f'Copying from {src} -> {dst}')
            shutil.copy(src, dst)

            txt_dst = dst.with_stem(f'{dst.stem}_info').with_suffix('.txt')
            with open(txt_dst, 'w', encoding='utf-8') as f:
                f.write(f"This is the 'original'.\n")
                f.write(f"All Duplicates\n")
                for path in paths:
                    f.write(f' - {path}\n')

        else:
            print(f'Creating txt file at {dst}')
            txt_dst = dst.with_stem(f'{dst.stem}_dup').with_suffix('.txt')
            with open(txt_dst, 'w', encoding='utf-8') as f:
                f.write(f"Duplicate of [{paths[0]}]\n")
                f.write(f"All Duplicates\n")
                for path in paths:
                    f.write(f' - {path}\n')






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