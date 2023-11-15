# songs download scripts

scripts to download from my playlist (<https://songsyt.netlify.app/>)

they require [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) to be installed and in path

## windows

`windows.bat` only downloads audio, thumbnails and metadata.

you need to put your own folder path and path to `config.txt` in the script.

## android

`android.sh` does what windows does, but is more opinionated. it downloads the songs to `/storage/emulated/0/music/songs`, prompts you to add replaygain tags, and adds playlist added date metadata with `add_playlist_added_date.py`. so make sure you have those installed and in path.

this script expects you to have `add_playlist_added_date.py` in `/storage/emulated/0/music` and a folder named `songs` in it.
