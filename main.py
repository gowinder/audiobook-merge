import os

from dotenv import load_dotenv
from mutagen.mp4 import MP4, MP4Tags
from pydub import AudioSegment
#from StringIO import StringIO
from io import BytesIO

# Load environment variables from .env file
load_dotenv()


def merge_audiobook_chapters(input_directory, output_file):
    # Get list of M4A files in the directory, sorted by filename
    files = sorted([f for f in os.listdir(input_directory) if f.endswith(".m4a")])

    # Initialize an empty AudioSegment for concatenation
    audiobook = AudioSegment.empty()

    # List to store chapter metadata
    chapters = []
    chapter_start = 0

    print(f"Merging {len(files)} chapters from {input_directory}")
    for file in files:
        # Load the audio file
        file_path = os.path.join(input_directory, file).encode("utf-8")
        print(f"Loading {file_path}")
        audio = AudioSegment.from_file(file_path, format="m4a")
        #audio = AudioSegment.from_raw(open(file_path),  sample_width=2,
        #                             sample_rate=44100, format="m4a", frame_rate=44100, channels=2)
        # Append to the audiobook
        audiobook += audio

        # Add chapter information
        chapter_duration = len(audio)
        chapters.append(
            (chapter_start, chapter_start + chapter_duration, os.path.splitext(file)[0])
        )
        chapter_start += chapter_duration

    # Export the merged audiobook
    output_path = os.path.join(input_directory, output_file)
    audiobook.export(output_path, format="mp4", codec="aac")

    # Add chapters to the M4B file
    add_chapters_to_audiobook(output_path, chapters)


def add_chapters_to_audiobook(file_path, chapters):
    # Load the exported audiobook file
    audio = MP4(file_path)

    # Add chapter metadata
    chapter_list = []
    for start, end, title in chapters:
        chapter_list.append((start / 1000, title))  # Convert milliseconds to seconds

    audio.tags = MP4Tags()
    audio.tags["©nam"] = "Audiobook"  # Set the title of the audiobook
    audio.tags["©ART"] = "Author"  # Set the author of the audiobook
    audio.tags["©alb"] = "Album"  # Set the album name of the audiobook
    audio.tags["©gen"] = "Audiobook"  # Set the genre
    audio.tags["trkn"] = [(1, 1)]  # Track number

    # Add chapters using the 'chpl' atom
    chpl = []
    for start, title in chapter_list:
        chpl.append(
            {
                "time": start,
                "title": title,
            }
        )
    audio.tags["chpl"] = chpl

    # Save the changes
    audio.save()


if __name__ == "__main__":
    input_directory = os.getenv("INPUT_DIRECTORY")
    output_file = os.getenv("OUTPUT_FILE")
    merge_audiobook_chapters(input_directory, output_file)
