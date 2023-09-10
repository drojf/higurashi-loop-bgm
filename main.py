import os
import pathlib
import hashlib
import pickle
from pathlib import Path
import shutil
import re
import csv

scan_folder = 'input'
output_dir = 'output'
out_csv_path = 'bgm-to-sha.csv'

def sha256sum(filename):
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def caculate_sha256_of_files_in_folder():
    if not os.path.exists(scan_folder):
        print(f"ERROR: input folder '{scan_folder}' missing!")
        exit(-1)
    

    shas = []

    # iterate through all original hou sprites and calculate their SHA256
    for path in pathlib.Path(scan_folder).rglob('*.*'):
        sha256 = sha256sum(path)
        relpath = path.relative_to(scan_folder)

        # print(f'{path} -> {sha256}')

        shas.append((relpath, sha256))

    return shas


mapping = caculate_sha256_of_files_in_folder()

with open(out_csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting = csv.QUOTE_ALL)
    for path, sha256 in mapping:
        writer.writerow([path, sha256])


unique_mapping = {}

dup_count = 0

for path, sha256 in mapping:
    if sha256 in unique_mapping:
        dup_count += 1
        if path not in unique_mapping[sha256]:
            unique_mapping[sha256][path] = None
    else:
        unique_mapping[sha256] = {path: {None}}

print(f"Found {dup_count} duplicates")

for key, value in unique_mapping.items():
    source = os.path.join(scan_folder, list(value)[0])
    dest = os.path.join(output_dir, list(value)[0])

    # print(f"{source} -> {dest}")
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(source, dest)