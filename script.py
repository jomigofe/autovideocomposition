import os
import subprocess
import random

def convert_list(lst):
    if not lst:
        return []
    
    result = [lst[0]]
    
    for i in range(1, len(lst)):
        result.append(lst[i] - lst[i-1])
        
    return result


def generate_timestamps(total_length, music_cues):
    num_clips = len(music_cues)

    clip_lengths = convert_list(music_cues)

    total_clips_length = sum(clip_lengths)
    
    # Calculate approximate gap between each clip if they were evenly spaced
    average_gap = (total_length - total_clips_length) / (num_clips + 1)

    start_times = []
    last_end_time = 0
    
    for i in range(num_clips):
        # Randomize within a margin around the average gap, say 20% of the average_gap
        margin = 0.2 * average_gap
        min_gap = int(average_gap - margin)
        max_gap = int(average_gap + margin)

        gap = random.randint(min_gap, max_gap)
        start = last_end_time + gap

        # If this pushes the last clip beyond total_length, adjust
        if i == num_clips - 1 and start + clip_lengths[i] > total_length:
            start = total_length - clip_lengths[i]
        
        start_times.append(start)
        last_end_time = start + clip_lengths[i]

    # Calculate end times for each clip
    end_times = [start_times[i] + clip_lengths[i] for i in range(num_clips)]
    
    return list(zip(start_times, end_times))

# # Test
# video_length = 331
# music_cues = [10, 20, 23, 15]
# print(generate_timestamps(video_length, music_cues))


def get_video_length(video_path):
    cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video_path}"
    output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
    return float(output)

# Paths
video_list_path = "path_to_video_list.txt"
audio_file_path = "path_to_audio.mp3"
timestamps_path = "path_to_timestamps.txt"

# Concatenate videos
concat_cmd = f"ffmpeg -y -f concat -safe 0 -i {video_list_path} -c copy merged_video.mp4"
subprocess.run(concat_cmd, shell=True)

# Get the merged video length
merged_video_length = get_video_length("merged_video.mp4")

# Get the beat timestamps
with open(timestamps_path, 'r') as f:
    timestamps = f.readlines()
timestamps = [float(t.strip()) for t in timestamps]

# Calculate intervals
clips_length = generate_timestamps(merged_video_length, timestamps)

# Extract clips from the merged video using the clip intervals
clips = []
for i, clip in enumerate(clips_length):
    start, end = clip
    clip_cmd = f"ffmpeg -y -i merged_video.mp4 -ss {start} -to {end} -c copy clip_{i}.mp4"
    subprocess.run(clip_cmd, shell=True)
    clips.append(f"clip_{i}.mp4")


# Concatenate clips
clips_text = "\n".join(["file '" + clip + "'" for clip in clips])
with open("clips_list.txt", "w") as f:
    f.write(clips_text)

concat_clips_cmd = "ffmpeg -y -f concat -safe 0 -i clips_list.txt -c copy final_no_audio.mp4"
subprocess.run(concat_clips_cmd, shell=True)

# Add audio
final_cmd = f"ffmpeg -y -i final_no_audio.mp4 -i {audio_file_path} -c:v copy -c:a aac -strict experimental final_video.mp4"
subprocess.run(final_cmd, shell=True)

# Optionally, delete intermediate files
os.remove("merged_video.mp4")
os.remove("final_no_audio.mp4")
for clip in clips:
    os.remove(clip)
