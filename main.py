import os
import time
from tempfile import NamedTemporaryFile

from dotenv import load_dotenv
from mutagen.mp4 import MP4, MP4Tags
from pydub import AudioSegment

# Load environment variables from .env file
load_dotenv()


def merge_audiobook_chapters(
    input_directory, output_file_prefix, max_duration=11 * 60 * 60 * 1000
):
    # Get list of M4A files in the directory, sorted by filename
    files = sorted([f for f in os.listdir(input_directory) if f.endswith(".m4a")])

    # List to store chapter metadata
    chapters = []
    chapter_start = 0
    part_number = 1

    print(f"Merging {len(files)} chapters from {input_directory}")

    audiobook = AudioSegment.empty()

    for file in files:
        # Load the audio file
        file_path = os.path.join(input_directory, file)
        print(f"Loading {file_path}")
        start_time = time.time()
        audio = AudioSegment.from_file(file_path, format="m4a")
        load_time = time.time() - start_time
        print(
            f"Loaded {audio.duration_seconds} seconds of audio in {load_time:.2f} seconds"
        )

        # Append to the current audiobook segment
        audiobook += audio

        # Add chapter information
        chapter_duration = len(audio)
        chapters.append(
            (chapter_start, chapter_start + chapter_duration, os.path.splitext(file)[0])
        )
        chapter_start += chapter_duration

        # Check if the current audiobook segment exceeds the maximum duration
        if len(audiobook) >= max_duration:
            # Export the current segment to an M4B file
            output_file = f"{output_file_prefix}_part{part_number}.m4b"
            output_path = os.path.join(input_directory, output_file)
            audiobook.export(output_path, format="m4b", codec="aac")
            add_chapters_to_audiobook(output_path, chapters)

            # Reset for the next segment
            audiobook = AudioSegment.empty()
            chapters = []
            chapter_start = 0
            part_number += 1

    # Export the last segment if there's any audio left
    if len(audiobook) > 0:
        output_file = f"{output_file_prefix}_part{part_number}.m4b"
        output_path = os.path.join(input_directory, output_file)
        audiobook.export(output_path, format="m4b", codec="aac")
        add_chapters_to_audiobook(output_path, chapters)


def add_chapters_to_audiobook(file_path, chapters):
    # Load the exported audiobook file
    audio = MP4(file_path)

    # Add chapter metadata
    chapter_list = []
    for start, end, title in chapters:
        chapter_list.append((start / 1000, title))  # Convert milliseconds to seconds

    audio.tags = MP4Tags()
    audio.tags["©nam"] = os.getenv("OUTPUT_FILE")  # Set the title of the audio「方案选单」book
    audio.tags["©ART"] = os.getenv("AB_AUTHOR")  # Set the author of the audiobook
    audio.tags["©alb"] = os.getenv("AB_ALBUM")  # Set the album name of the audiobook
    audio.tags["©gen"] = os.getenv("AB_GENRE")  # Set the genre
    audio.tags["trkn"] = [(1, 1)]  # Track number

    # Add chapters using the 'chpl' atom
    chpl = []
    for start, title in chapter_list:
        chpl.append({"time": start, "title": title})
    audio.tags["chpl"] = chpl

    # Save the changes
    audio.save()


if __name__ == "__main__":
    input_directory = os.getenv("INPUT_DIRECTORY")
    output_file_prefix = os.getenv("OUTPUT_FILE_PREFIX")
    merge_audiobook_chapters(input_directory, output_file_prefix)
