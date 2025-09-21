import argparse

from bye_cloud.utils import (
    extract_albums,
    extract_icloud_zips,
    extract_memories,
    extract_photos,
    extract_shared_albums,
    remove_temp_dir,
)


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
