import argparse
import glob
import os
import re
from pathlib import Path
from typing import Mapping, MutableMapping, Set

import requests
from isodate import parse_datetime


def check_plural(number: int, plural: str, single: str = "") -> str:
    return single if number == 1 else plural


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


def add_metadata_to_directory(
    directory: str, delete: bool, missing: bool, delete_all: bool
):
    api = "https://raw.githubusercontent.com/RealCyGuy/songs-backup/main/output/summary.json"
    data = requests.get(api).json()
    songs_data = {}
    for song in data["items"]:
        songs_data[song["id"]] = song

    songs = glob.iglob(os.path.join(directory, "*.mp3"))
    print(f"Loaded {len(songs_data)} songs from {api}")

    missing_songs = set()
    if missing:
        missing_songs = set(songs_data.keys())

    skipped = 0
    updated = 0
    delete_songs = {}
    with open(os.path.join(directory, "added_playlist_date.txt"), "a+") as archive:
        archive.seek(0)
        added = archive.read().splitlines()
        print(f"Loaded {len(added)} lines from {archive.name}\n")
        for file in songs:
            path = Path(file)
            search = None
            for s in re.finditer(r"(?<=\[)([A-Za-z0-9_\-]*)(?=])", path.stem):
                search = s
            if search is None:
                print(f"Warning: Couldn't find a video id in {file}")
                continue
            video_id = search.group()
            song_data = songs_data.get(video_id)
            if song_data is None:
                print(f"Warning: Couldn't find song data for {file}")
                delete_songs[video_id] = file
                continue
            if missing:
                missing_songs.discard(video_id)
            if video_id in added:
                skipped += 1
                continue
            os.utime(
                file,
                times=(
                    os.stat(file).st_atime,
                    parse_datetime(song_data["addedDate"]).timestamp(),
                ),
            )
            print(f"Updated modified time for {path}")
            archive.write(video_id + "\n")
            updated += 1
    print(
        f"\n{updated} file{check_plural(updated, 's')} {check_plural(updated, 'were', 'was')} updated, "
        f"{skipped} file{check_plural(skipped, 's')} {check_plural(skipped, 'were', 'was')} skipped."
    )
    if missing:
        show_missing(missing_songs, songs_data)
    if delete_all:
        delete_all_songs(delete_songs)
    elif delete:
        delete_menu(delete_songs)


def delete_menu(songs: MutableMapping[str, str]) -> None:
    if len(songs) == 0:
        print("\nNo songs to delete.")
        return
    print("\nThese are songs that I couldn't find song data for:\n")
    width = len(max(songs.keys(), key=lambda x: len(x)))
    for video_id, name in songs.items():
        print(f"{video_id.rjust(width)} - {name}")
    print(
        '\nInput the ID of videos you want to delete from this device. Type "c" or nothing to cancel.\n'
    )
    while True:
        video_id = input("> ").strip()
        if video_id == "c" or len(video_id) == 0:
            break
        if video_id in songs.keys():
            name = songs[video_id]
            try:
                os.remove(name)
            except Exception as e:
                print(e)
                break
            else:
                print(f"Successfully deleted {name}")
                del songs[video_id]
        else:
            print(f"Video id {video_id} is not in the list!")


def delete_all_songs(songs: MutableMapping[str, str]) -> None:
    if len(songs) == 0:
        print("\nNo songs to delete.")
        return
    check = input(
        f"\nAre you sure you want to {len(songs)} song{check_plural(len(songs), 's')} without data? (y/n) "
    )
    print()
    if check.lower() == "y":
        for video_id, name in songs.items():
            try:
                os.remove(name)
            except Exception as e:
                print(e)
                break
            else:
                print(f"Successfully deleted {name}")
        print(
            f"\nDeleted {len(songs)} song{check_plural(len(songs), 's')} without data."
        )
    else:
        print("Cancelled.")


def show_missing(missing_songs: Set[str], songs_data: Mapping[str, dict]) -> None:
    print("\nThese songs aren't downloaded yet:\n")
    for song in missing_songs:
        data = songs_data[song]
        print(f"{data['title']} by {data['channel']} [{data['id']}]")
    print()


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("path", help="path to songs directory", type=dir_path)
    argParser.add_argument(
        "--delete",
        "-d",
        action="store_true",
        help="show an interface for deleting songs without data",
    )
    argParser.add_argument(
        "--missing",
        "-m",
        action="store_true",
        help="list songs that aren't found",
    )
    argParser.add_argument(
        "--delete-all",
        action="store_true",
        help="delete all songs without data",
    )

    args = argParser.parse_args()
    add_metadata_to_directory(args.path, args.delete, args.missing, args.delete_all)
