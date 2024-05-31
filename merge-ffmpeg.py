import os
import re
import subprocess
import time

from dotenv import load_dotenv
from mutagen.mp4 import MP4

load_dotenv()


def create_concat_file(input_directory, concat_file_path):
    files = sorted(
        [f for f in os.listdir(input_directory) if f.endswith(".m4a")],
        key=lambda x: int(re.findall(r"^\d+", x)[0]),
    )
    with open(concat_file_path, "w") as f:
        for file in files:
            file_path = os.path.join(input_directory, file)
            f.write(f"file '{file_path}'\n")


def merge_audiobook_chapters(input_directory, output_file):
    concat_file = os.path.join(input_directory, "concat_list.txt")
    create_concat_file(input_directory, concat_file)

    command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        output_file,
    ]

    subprocess.run(command, check=True)

    # Clean up the temporary concat file
    os.remove(concat_file)


def generate_chapters_file(input_directory, chapters_file_path):
    files = sorted(
        [f for f in os.listdir(input_directory) if f.endswith(".m4a")],
        key=lambda x: int(re.findall(r"^\d+", x)[0]),
    )
    with open(chapters_file_path, "w") as f:
        f.write(";FFMETADATA1\n")  # 添加 FFMETADATA1 标记
        start = 0
        for i, file in enumerate(files):
            file_path = os.path.join(input_directory, file)
            audio = MP4(file_path)
            duration = int(audio.info.length)
            end = start + duration * 1000  # Convert seconds to milliseconds

            # 写入 FFMETADATA 格式的章节信息
            f.write(
                f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={start}\nEND={end}\ntitle=Chapter {i + 1}\n\n"
            )
            start = end


def add_chapters_to_m4b(m4b_file, chapters_file, output_file):
    command = [
        "ffmpeg",
        "-i",
        m4b_file,
        "-i",
        chapters_file,
        "-map_metadata",
        "1",
        "-map",
        "0",
        "-c",
        "copy",
        "-metadata:s:v:0",
        'title="Chapters"',
        output_file,
    ]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    input_directory = os.getenv("INPUT_DIRECTORY")
    output_file = os.getenv("OUTPUT_FILE")
    delete_internal_file = os.getenv("DELETE_INTERNAL_FILE", "false").lower() == "true"
    chapters_file = "chapters.txt"

    # Generate final output file name
    base, ext = os.path.splitext(output_file)
    final_output_file = f"{base}.chapters{ext}"

    # Step 1: Merge m4a files into one m4b file
    merge_audiobook_chapters(input_directory, output_file)

    # Step 2: Generate chapters file based on m4a file names and durations
    generate_chapters_file(input_directory, chapters_file)

    # Step 3: Add chapters to the merged m4b file
    add_chapters_to_m4b(output_file, chapters_file, final_output_file)

    # Step 4: Delete the original output file if DELETE_INTERNAL_FILE is true
    if delete_internal_file:
        os.remove(output_file)
