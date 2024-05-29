from pydub.utils import mediainfo


def get_audio_info(file_path):
    audio_info = mediainfo(file_path)
    print(audio_info)
    sample_width = audio_info['sample_width']
    frame_rate = audio_info['sample_rate']
    channels = audio_info['channels']
    return sample_width, frame_rate, channels


file_path = '/Users/destroyer/Downloads/wanming/1.m4a'
sample_width, frame_rate, channels = get_audio_info(file_path)
print("Sample Width:", sample_width)
print("Frame Rate:", frame_rate)
print("Channels:", channels)
)