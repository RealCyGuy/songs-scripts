import argparse
import glob
import os
import re
from pathlib import Path

import requests
from isodate import parse_datetime


def check_plural(number: int, plural: str, single: str = "") -> str:
    return single if number == 1 else plural


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def add_metadata_to_directory(directory: str):
    api = "https://raw.githubusercontent.com/RealCyGuy/songs-backup/main/output/summary.json"
    data = requests.get(api).json()
    songs_data = {}
    for song in data["items"]:
        songs_data[song["id"]] = song

    songs = glob.iglob(os.path.join(directory, "*.mp3"))
    print(f"Loaded {len(songs_data)} songs from {api}")

    skipped = 0
    updated = 0
    with open(os.path.join(directory, "added_playlist_date.txt"), "a+") as archive:
        archive.seek(0)
        added = archive.read().splitlines()
        print(f"Loaded {len(added)} lines from {archive.name}\n")
        for file in songs:
            path = Path(file)
            search = re.search(r"(?<=\[)([A-Za-z0-9_\-]*)(?=])", path.stem)
            if search is None:
                print(f"Warning: Couldn't find a video id in {file}")
                continue
            video_id = search.group()
            song_data = songs_data.get(video_id)
            if song_data is None:
                print(f"Warning: Couldn't find song data for {file}")
                continue
            if video_id in added:
                skipped += 1
                continue
            os.utime(file, times=(os.stat(file).st_atime, parse_datetime(song_data["addedDate"]).timestamp()))
            print(f"Updated modified time for {path}")
            archive.write(video_id + "\n")
            updated += 1
    print(f"\n{updated} file{check_plural(updated, 's')} {check_plural(updated, 'were', 'was')} updated, "
          f"{skipped} file{check_plural(skipped, 's')} {check_plural(skipped, 'were', 'was')} skipped.")


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("path", help="path to songs directory", type=dir_path)

    args = argParser.parse_args()
    add_metadata_to_directory(args.path)
