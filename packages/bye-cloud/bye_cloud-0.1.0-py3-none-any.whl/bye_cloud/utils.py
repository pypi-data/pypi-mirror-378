"""
bye-cloud - convert iCould exports to a more useful format.
"""

import os
import csv
from tqdm import tqdm
import time
import random

import shutil
import hashlib

import zipfile
import glob
import re


def unzip_icloud_shared_albums(source, dest):
    # Create the destination directory if it does not exist
    os.makedirs(dest, exist_ok=True)

    # Construct the pattern for the zip files
    pattern = os.path.join(source, "iCloud Shared Albums*.zip")

    # Find all zip files matching the pattern
    zip_files = glob.glob(pattern)

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(dest)
            print(f"Extracted: {zip_file} to {dest}")


def generate_nonce():
    """Generate a unique nonce using the current timestamp and a random number."""
    timestamp = int(time.time())  # Current time in seconds
    random_number = random.randint(1000, 9999)  # Random number between 1000 and 9999
    return f"{timestamp}_{random_number}"


def new_filename(file_path, nonce=None):
    """
    Insert a value between the file name and its extension in a complete file path.

    :param file_path: The complete file path (e.g., 'path/to/file.jpg').
    :param value: The value to insert (e.g., 'some_value').
    :return: The modified file path with the value inserted.
    """
    # Split the file path into directory, file name, and extension
    directory, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)

    if hash is not None:
        nonce = hash
    else:
        nonce = generate_nonce()

    # Create the new filename with the value inserted
    new_filename = f"{name}_{nonce}{ext}"

    # Combine the directory and the new filename
    new_file_path = os.path.join(directory, new_filename)

    return new_file_path


def check_details(unzipped):
    pass  # Stub for checking metadata details


def extract_photos(unzipped, dest):
    """
    Extract photos from {unzipped} to {dest}/Photos

    Creates {dest}/Photos directory if it does not exist
    Copies all files from {unzipped/Photos} to {dest/Photos}.
        If a file already exists, check the hash of each photo
        If the files have the same hash, skip
        If the files differ, issue a warning that the file name is already in
        use with another image.
    Calls check_details(unzipped) to check all of the metadata details
    """
    photos_source = os.path.join(unzipped, "Photos")
    photos_dest = os.path.join(dest, "Photos")

    print(photos_source, photos_dest)
    # Create the destination Photos directory if it does not exist
    os.makedirs(photos_dest, exist_ok=True)

    warnings = []

    # Iterate over all files in the source Photos directory
    files = os.listdir(photos_source)
    for filename in tqdm(files, desc="Copying photos"):
        source_file = os.path.join(photos_source, filename)
        if source_file.endswith(".csv"):
            continue
        dest_file = os.path.join(photos_dest, filename)

        if os.path.isfile(source_file):
            if os.path.exists(dest_file):
                # Check if the files have the same hash'
                source_file_hash = file_hash(source_file)
                if file_hash(source_file) == file_hash(dest_file):
                    continue  # Skip if the files are the same
                else:
                    dest_file = new_filename(dest_file, source_file_hash)
                    warnings.append(
                        f"Warning: {filename} already exists with a different image. Changed to {dest_file}"
                    )

            # Copy the file to the destination
            shutil.copy2(source_file, dest_file)

    if len(warnings) > 0:
        print(f"Warnings ({len(warnings)}):")
        for warning in warnings:
            print(warning)

    # Call check_details to check all of the metadata details
    check_details(unzipped)


def file_hash(file_path):
    """Calculate the hash of a file using SHA-256."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def extract_albums(unzipped, dest, album_dir_name="Albums"):
    """
    Extract Albums

    Iterate through all .csv files in {unzipped}/Albums.
    Use the name of the .csv file (minus ".csv") as the Album name.
    The CSV only has one column.
    The first row is just a heading with the word "Images". Ignore this.
    For all the remaining rows, use the value of the cell as the file name
    and make a hard link to this file in dest/Albums/{album_name}/{file_name}.
    Creates the directories Albums/{album_name} if they do not exist.
    """
    albums_dir = os.path.join(unzipped, album_dir_name)

    if not os.path.exists(albums_dir):
        print(f"No {album_dir_name} information in {unzipped}.")
        return

    warnings = []
    # Iterate through all .csv files in the Albums directory
    for csv_file in tqdm(os.listdir(albums_dir), desc=f"Processing {album_dir_name}"):
        if csv_file.endswith(".csv"):
            album_name = csv_file[:-4]  # Remove the ".csv" extension
            album_path = os.path.join(dest, album_dir_name, album_name)

            # Create the album directory if it does not exist
            os.makedirs(album_path, exist_ok=True)

            # Read the CSV file, ignoring the first row
            csv_path = os.path.join(albums_dir, csv_file)
            with open(csv_path, mode="r", newline="") as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row

                # Iterate through the rows in the CSV
                for row in tqdm(reader, desc=f"Linking images in {album_name}"):
                    file_name = row[0]  # Get the file name from the first column
                    source_file = os.path.join(
                        dest, "Photos", file_name
                    )  # Full path to the source file
                    dest_file = os.path.join(
                        album_path, file_name
                    )  # Destination path for the hard link

                    # Check if the destination file already exists
                    if os.path.exists(dest_file):
                        # Compare hash values
                        dest_file_hash = file_hash(dest_file)
                        source_file_hash = file_hash(source_file)
                        if dest_file_hash != source_file_hash:

                            # Change the destination file name
                            dest_file = new_filename(dest_file, source_file)
                            warnings.append(
                                f"Duplicate file name:'{file_name}' - Changing name to {dest_file}"
                            )

                        else:
                            # If the hashes match, we can skip linking
                            continue

                    # Create a hard link to the file in the album directory
                    try:
                        os.link(source_file, dest_file)
                    except FileExistsError:
                        # If the link already exists, you can choose to ignore or handle it
                        pass

                if len(warnings) > 0:
                    print(f"Warnings ({len(warnings)}):")
                    for warning in warnings:
                        print(warning)


def extract_shared_albums(unzipped, dest):
    """
    Shared albums are just zips of folders with images, no spreadsheet stuff to process.
    """
    unzip_icloud_shared_albums(unzipped, dest)


def extract_memories(unzipped, dest):
    """
    Extract Memories

    Thin wrapper for extrac_albums because Memories are stored in the same format as Albums.
    """
    extract_albums(unzipped, dest, album_dir_name="Memories")


def export(source, dest):

    # Call the extraction functions
    extract_photos(source, dest)
    extract_albums(source, dest)
    extract_shared_albums(source, dest)
    extract_memories(source, dest)


def discover_icloud_zips(source):

    # Construct the pattern for the zip files
    pattern = os.path.join(source, "iCloud Photos Part * of *.zip")

    # Use glob to find all matching files
    matching_files = glob.glob(pattern)

    # Extract just the file names from the full paths
    matching_file_names = [os.path.basename(file) for file in matching_files]

    # Check for expected number of zip files based on the file names
    expected_count = 0
    for filename in matching_file_names:
        match = re.search(r"iCloud Photos Part \d+ of (\d+)\.zip", filename)
        if match:
            expected_count = max(expected_count, int(match.group(1)))

    # Check if the expected count matches the found count
    found_count = len(matching_file_names)
    if expected_count > found_count:
        print(
            f"Based on the file names, we expect there to be a total of {expected_count} zip files, but we found {found_count}. The import will likely fail."
        )
        user_input = input("Would you like to continue anyway? (y/N): ")
        if user_input.lower() != "y":
            print("Operation cancelled.")
            return []

    return matching_file_names


def extract_icloud_zips(source, dest):
    """
    Unzip iCloud zip files to temp directory in export directory
    """

    # Discover the iCloud zip files
    zip_files = discover_icloud_zips(source)

    zip_dest = os.path.join(dest, "temp")

    # Create the destination directory if it does not exist
    os.makedirs(zip_dest, exist_ok=True)

    unzipped_files = []

    for zip_file in zip_files:
        zip_file_path = os.path.join(source, zip_file)
        print(f"Unzipping {zip_file_path}...")

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(zip_dest)
            # Get the list of extracted files

            # Add the unzipped file name without the .zip extension
            unzipped_file_name = os.path.splitext(os.path.basename(zip_file_path))[
                0
            ]  # Remove .zip extension
            unzipped_files.append(os.path.join(zip_dest, unzipped_file_name))

    return unzipped_files


def remove_temp_dir(dest):
    """
    Remove the temp directory where files are unzipped for staging
    """

    # Check if the directory exists
    print(f"Cleaning up temporary files...")
    if os.path.exists(dest):
        # Remove the directory and all its contents
        shutil.rmtree(dest)
        print(f"Successfully deleted the directory: {dest}")
    else:
        print(f"The directory {dest} does not exist.")


def main():
    parser = argparse.ArgumentParser(
        description="bye-cloud - Export iCloud Photos archive to something useful"
    )

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="A directory containing all 'iCloud Photos Part X of Y.zip'",
    )

    parser.add_argument(
        "-o", "--output", required=True, help="Path where export should be created"
    )

    args = parser.parse_args()

    parts = extract_icloud_zips(args.input, args.output)

    for part in parts:
        extract_photos(part, args.output)

    for part in parts:
        extract_albums(part, args.output)

    for part in parts:
        extract_memories(part, args.output)

    for part in parts:
        extract_shared_albums(part, args.output)

    # Delete the unzipped files
    remove_temp_dir(os.path.join(args.output, "temp"))


if __name__ == "__main__":
    main()
"""
bye-cloud - convert iCould exports to a more useful format.
"""

import argparse

import os
import csv
from tqdm import tqdm
import time
import random

import shutil
import hashlib

import zipfile
import glob
import re


def unzip_icloud_shared_albums(source, dest):
    # Create the destination directory if it does not exist
    os.makedirs(dest, exist_ok=True)

    # Construct the pattern for the zip files
    pattern = os.path.join(source, "iCloud Shared Albums*.zip")

    # Find all zip files matching the pattern
    zip_files = glob.glob(pattern)

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(dest)
            print(f"Extracted: {zip_file} to {dest}")


def generate_nonce():
    """Generate a unique nonce using the current timestamp and a random number."""
    timestamp = int(time.time())  # Current time in seconds
    random_number = random.randint(1000, 9999)  # Random number between 1000 and 9999
    return f"{timestamp}_{random_number}"


def new_filename(file_path, nonce=None):
    """
    Insert a value between the file name and its extension in a complete file path.

    :param file_path: The complete file path (e.g., 'path/to/file.jpg').
    :param value: The value to insert (e.g., 'some_value').
    :return: The modified file path with the value inserted.
    """
    # Split the file path into directory, file name, and extension
    directory, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)

    if hash is not None:
        nonce = hash
    else:
        nonce = generate_nonce()

    # Create the new filename with the value inserted
    new_filename = f"{name}_{nonce}{ext}"

    # Combine the directory and the new filename
    new_file_path = os.path.join(directory, new_filename)

    return new_file_path


def check_details(unzipped):
    pass  # Stub for checking metadata details


def extract_photos(unzipped, dest):
    """
    Extract photos from {unzipped} to {dest}/Photos

    Creates {dest}/Photos directory if it does not exist
    Copies all files from {unzipped/Photos} to {dest/Photos}.
        If a file already exists, check the hash of each photo
        If the files have the same hash, skip
        If the files differ, issue a warning that the file name is already in
        use with another image.
    Calls check_details(unzipped) to check all of the metadata details
    """
    photos_source = os.path.join(unzipped, "Photos")
    photos_dest = os.path.join(dest, "Photos")

    print(photos_source, photos_dest)
    # Create the destination Photos directory if it does not exist
    os.makedirs(photos_dest, exist_ok=True)

    warnings = []

    # Iterate over all files in the source Photos directory
    files = os.listdir(photos_source)
    for filename in tqdm(files, desc="Copying photos"):
        source_file = os.path.join(photos_source, filename)
        if source_file.endswith(".csv"):
            continue
        dest_file = os.path.join(photos_dest, filename)

        if os.path.isfile(source_file):
            if os.path.exists(dest_file):
                # Check if the files have the same hash'
                source_file_hash = file_hash(source_file)
                if file_hash(source_file) == file_hash(dest_file):
                    continue  # Skip if the files are the same
                else:
                    dest_file = new_filename(dest_file, source_file_hash)
                    warnings.append(
                        f"Warning: {filename} already exists with a different image. Changed to {dest_file}"
                    )

            # Copy the file to the destination
            shutil.copy2(source_file, dest_file)

    if len(warnings) > 0:
        print(f"Warnings ({len(warnings)}):")
        for warning in warnings:
            print(warning)

    # Call check_details to check all of the metadata details
    check_details(unzipped)


def file_hash(file_path):
    """Calculate the hash of a file using SHA-256."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def extract_albums(unzipped, dest, album_dir_name="Albums"):
    """
    Extract Albums

    Iterate through all .csv files in {unzipped}/Albums.
    Use the name of the .csv file (minus ".csv") as the Album name.
    The CSV only has one column.
    The first row is just a heading with the word "Images". Ignore this.
    For all the remaining rows, use the value of the cell as the file name
    and make a hard link to this file in dest/Albums/{album_name}/{file_name}.
    Creates the directories Albums/{album_name} if they do not exist.
    """
    albums_dir = os.path.join(unzipped, album_dir_name)

    if not os.path.exists(albums_dir):
        print(f"No {album_dir_name} information in {unzipped}.")
        return

    warnings = []
    # Iterate through all .csv files in the Albums directory
    for csv_file in tqdm(os.listdir(albums_dir), desc=f"Processing {album_dir_name}"):
        if csv_file.endswith(".csv"):
            album_name = csv_file[:-4]  # Remove the ".csv" extension
            album_path = os.path.join(dest, album_dir_name, album_name)

            # Create the album directory if it does not exist
            os.makedirs(album_path, exist_ok=True)

            # Read the CSV file, ignoring the first row
            csv_path = os.path.join(albums_dir, csv_file)
            with open(csv_path, mode="r", newline="") as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row

                # Iterate through the rows in the CSV
                for row in tqdm(reader, desc=f"Linking images in {album_name}"):
                    file_name = row[0]  # Get the file name from the first column
                    source_file = os.path.join(
                        dest, "Photos", file_name
                    )  # Full path to the source file
                    dest_file = os.path.join(
                        album_path, file_name
                    )  # Destination path for the hard link

                    # Check if the destination file already exists
                    if os.path.exists(dest_file):
                        # Compare hash values
                        dest_file_hash = file_hash(dest_file)
                        source_file_hash = file_hash(source_file)
                        if dest_file_hash != source_file_hash:

                            # Change the destination file name
                            dest_file = new_filename(dest_file, source_file)
                            warnings.append(
                                f"Duplicate file name:'{file_name}' - Changing name to {dest_file}"
                            )

                        else:
                            # If the hashes match, we can skip linking
                            continue

                    # Create a hard link to the file in the album directory
                    try:
                        os.link(source_file, dest_file)
                    except FileExistsError:
                        # If the link already exists, you can choose to ignore or handle it
                        pass

                if len(warnings) > 0:
                    print(f"Warnings ({len(warnings)}):")
                    for warning in warnings:
                        print(warning)


def extract_shared_albums(unzipped, dest):
    """
    Shared albums are just zips of folders with images, no spreadsheet stuff to process.
    """
    unzip_icloud_shared_albums(unzipped, dest)


def extract_memories(unzipped, dest):
    """
    Extract Memories

    Thin wrapper for extrac_albums because Memories are stored in the same format as Albums.
    """
    extract_albums(unzipped, dest, album_dir_name="Memories")


def export(source, dest):

    # Call the extraction functions
    extract_photos(source, dest)
    extract_albums(source, dest)
    extract_shared_albums(source, dest)
    extract_memories(source, dest)


def discover_icloud_zips(source):

    # Construct the pattern for the zip files
    pattern = os.path.join(source, "iCloud Photos Part * of *.zip")

    # Use glob to find all matching files
    matching_files = glob.glob(pattern)

    # Extract just the file names from the full paths
    matching_file_names = [os.path.basename(file) for file in matching_files]

    # Check for expected number of zip files based on the file names
    expected_count = 0
    for filename in matching_file_names:
        match = re.search(r"iCloud Photos Part \d+ of (\d+)\.zip", filename)
        if match:
            expected_count = max(expected_count, int(match.group(1)))

    # Check if the expected count matches the found count
    found_count = len(matching_file_names)
    if expected_count > found_count:
        print(
            f"Based on the file names, we expect there to be a total of {expected_count} zip files, but we found {found_count}. The import will likely fail."
        )
        user_input = input("Would you like to continue anyway? (y/N): ")
        if user_input.lower() != "y":
            print("Operation cancelled.")
            return []

    return matching_file_names


def extract_icloud_zips(source, dest):
    """
    Unzip iCloud zip files to temp directory in export directory
    """

    # Discover the iCloud zip files
    zip_files = discover_icloud_zips(source)

    zip_dest = os.path.join(dest, "temp")

    # Create the destination directory if it does not exist
    os.makedirs(zip_dest, exist_ok=True)

    unzipped_files = []

    for zip_file in zip_files:
        zip_file_path = os.path.join(source, zip_file)
        print(f"Unzipping {zip_file_path}...")

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(zip_dest)
            # Get the list of extracted files

            # Add the unzipped file name without the .zip extension
            unzipped_file_name = os.path.splitext(os.path.basename(zip_file_path))[
                0
            ]  # Remove .zip extension
            unzipped_files.append(os.path.join(zip_dest, unzipped_file_name))

    return unzipped_files


def remove_temp_dir(dest):
    """
    Remove the temp directory where files are unzipped for staging
    """

    # Check if the directory exists
    print(f"Cleaning up temporary files...")
    if os.path.exists(dest):
        # Remove the directory and all its contents
        shutil.rmtree(dest)
        print(f"Successfully deleted the directory: {dest}")
    else:
        print(f"The directory {dest} does not exist.")
