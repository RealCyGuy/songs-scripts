#!/bin/sh
cd /storage/emulated/0/music/songs 
yt-dlp --extract-audio --audio-format mp3 -o "%(title)s [%(id)s].%(ext)s" --download-archive archive.txt --rm-cache-dir https://www.youtube.com/playlist?list=PLRct1-5In-8Ewg5Kq-0JP8wh3ZweOXH9A --playlist-reverse --audio-quality 0 --add-metadata --parse-metadata "uploader:%(meta_artist)s" --parse-metadata "title:%(meta_title)s" --parse-metadata ":(?P<meta_purl>)" --parse-metadata "id:%(meta_comment)s" --parse-metadata ":(?P<meta_synopsis>)" --parse-metadata ":(?P<meta_description>)" --embed-thumbnail --convert-thumbnails jpg --ppa "EmbedThumbnail+ffmpeg_o:-c:v png -vf crop=\"'if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'\""
read -p "Run a ReplayGain scanner. (like foobar2000's) "
cd ..
python add_playlist_added_date.py songs --delete-all -m
