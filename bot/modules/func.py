#!/usr/bin/env python3
from re import findall as refindall
from subprocess import run as srun, check_output as scheck_output
from os import remove as osremove, rename as osrename, path as ospath

from bot import LOGGER, user_data


async def edit_video_titles(user_id, file_path):
    if not file_path.lower().endswith(('.mp4', '.mkv')):
        return
    user_dict = user_data.get(user_id, {})
    if user_dict.get("metadata", False):
        new_title = user_dict["metadata"]
        directory = ospath.dirname(file_path)
        file_name = ospath.basename(file_path)
        new_file = ospath.join(directory, f"new_{file_name}")
        LOGGER.info(f"Editing videos metadata title")
        command_probe = ["ffprobe", "-v", "error", "-show_entries", "stream=index", "-select_streams", "a", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        try:
            probe_result = scheck_output(command_probe).decode("utf-8").strip()
            audio_stream_count = len(refindall(r'\d+', probe_result))
        except:
            audio_stream_count = 0
        
        command_probe_subtitles = ["ffprobe", "-v", "error", "-show_entries", "stream=index", "-select_streams", "s", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        try:
            probe_result_subtitles = scheck_output(command_probe_subtitles).decode("utf-8").strip()
            subtitle_stream_count = len(refindall(r'\d+', probe_result_subtitles))
        except:
            subtitle_stream_count = 0

        cmd = ["ffmpeg", "-i", file_path, "-map", "0", "-c", "copy"]
        cmd += ["-metadata:s:v:0", f"title={new_title}"]
        for i in range(audio_stream_count):
            cmd += ["-metadata:s:a:{}".format(i), f"title={new_title}"]
        for i in range(subtitle_stream_count):
            cmd += ["-metadata:s:s:{}".format(i), f"title={new_title}"]

        cmd += ["-metadata", f"title={new_title}"]
        cmd.append(new_file)
        srun(cmd, check=True)
        osremove(file_path)
        osrename(new_file, f"{directory}/{file_name}")
