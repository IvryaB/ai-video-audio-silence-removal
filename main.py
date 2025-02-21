import moviepy.editor as mp
from pydub import AudioSegment, silence
import whisper
import re


def detect_silences(audio_path, min_silence_len=1000, silence_thresh=-50):
    """Detect pauses in audio and get their time intervals."""
    print("Detecting pauses in audio...")
    audio = AudioSegment.from_file(audio_path)
    silences = silence.detect_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    # Convert milliseconds to seconds
    silences = [
        (start / 1000.0, end / 1000.0)
        for start, end in silences
    ]
    print("Detected pauses:", silences)
    return silences  # Return the result


def transcribe_audio_with_whisper(audio_path, model_name="small", device="cuda"):
    """Optimized transcription of audio using Whisper."""
    print(f"Loading Whisper model ({model_name})...")
    model = whisper.load_model(model_name, device=device)
    print("Transcribing speech...")
    result = model.transcribe(
        audio_path,
        word_timestamps=True,
        language='uk',
        condition_on_previous_text=False,
        verbose=False
    )
    print("Transcription completed.")
    return result  # Return the transcription result


def get_filler_word_intervals(result, filler_word_patterns):
    """Get the time intervals for filler words from the Whisper transcription."""
    print("Identifying filler words in the transcription...")
    filler_intervals = []
    segments = result['segments']
    for segment in segments:
        words = segment['words']
        for word_info in words:
            word = word_info['word'].strip().lower()
            # Remove punctuation for accurate comparison
            word_clean = re.sub(r'[^\w\s]', '', word)
            # Check for filler words
            if any(re.fullmatch(pattern, word_clean) for pattern in filler_word_patterns):
                start = word_info['start']
                end = word_info['end']
                filler_intervals.append((start, end))
    print("Filler word intervals:", filler_intervals)
    return filler_intervals  # Return the list of filler word intervals


def combine_intervals(silences, fillers, buffer=0.1):
    """Combine and merge overlapping intervals with buffer time."""
    # Add buffer to each interval
    intervals = []
    for start, end in silences + fillers:
        intervals.append((max(0, start - buffer), end + buffer))

    # Sort intervals by start time
    intervals.sort(key=lambda x: x[0])

    # Merge overlapping intervals
    merged_intervals = []
    for current in intervals:
        if not merged_intervals:
            merged_intervals.append(current)
        else:
            prev_start, prev_end = merged_intervals[-1]
            curr_start, curr_end = current
            if curr_start <= prev_end:
                # Overlapping intervals, merge them
                merged_intervals[-1] = (prev_start, max(prev_end, curr_end))
            else:
                merged_intervals.append(current)
    print("Merged intervals for removal:", merged_intervals)
    return merged_intervals  # Return the merged intervals


def remove_intervals_from_audio_video(video_path, intervals_to_remove, output_video_path):
    """Remove specified intervals from audio and video with smooth transitions."""
    print("Removing intervals from audio and video with smooth transitions...")
    video = mp.VideoFileClip(video_path)

    # Create a list of included clips
    included_clips = []
    last_end = 0
    crossfade_duration = 0.2  # Set the crossfade duration (e.g., 0.2 seconds)

    for start, end in intervals_to_remove:
        if start > last_end:
            # Include segment before this interval
            clip = video.subclip(last_end, start)
            included_clips.append(clip)
        last_end = end

    if last_end < video.duration:
        # Include the remaining part of the video
        clip = video.subclip(last_end, video.duration)
        included_clips.append(clip)

    # Apply crossfades between clips
    if len(included_clips) > 1:
        clips_with_fades = []
        for i, clip in enumerate(included_clips):
            if i > 0:
                # Apply crossfadein to each clip except the first
                clip = clip.crossfadein(crossfade_duration)
            clips_with_fades.append(clip)
        final_clip = mp.concatenate_videoclips(clips_with_fades, method='compose')
    else:
        final_clip = included_clips[0]

    final_clip.write_videofile(
        output_video_path,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k"
    )
    print("Final video saved:", output_video_path)


# File paths
video_path = "input_video.mp4"
audio_path = "extracted_audio.wav"  # Use WAV for better quality
output_video_path = "output_video.mp4"

# Step 1: Extract audio from video
print("Extracting audio from video...")
video = mp.VideoFileClip(video_path)
video.audio.write_audiofile(audio_path)

# Step 2: Detect pauses and get their intervals
silence_intervals = detect_silences(
    audio_path,
    min_silence_len=1000,  # Increase the minimum silence length to 1 second
    silence_thresh=-50  # Lower the silence threshold for more accurate detection
)

# Step 3: Transcribe audio with Whisper and get filler word intervals
result = transcribe_audio_with_whisper(
    audio_path,
    model_name="small",
    device="cuda"
)

# List of filler words with various spellings and repeated letters
filler_word_patterns = [
    r'а+',  # 'а', 'аа', 'ааа', ...
    r'э+',  # 'э', 'ээ', 'эээ', ...
    r'м+',  # 'м', 'мм', 'ммм', ...
    r'ну+',
    r'як\s?би',
    r'взагал[іь]+',
    r'типу+',
    r'коротше+',
    r'це+',
    r'таке+',
    r'там+',
    r'отже+',
    r'значить+',
    r'вот+',
    r'собственно+',
    r'как\s?бы',
    r'мм+',
    r'блин+',
    r'слушай+',
    r'смотри+'
]

# Step 4: Get filler word intervals
filler_intervals = get_filler_word_intervals(result, filler_word_patterns)

# Step 5: Combine intervals with buffer
intervals_to_remove = combine_intervals(
    silence_intervals,
    filler_intervals,
    buffer=0.1  # Add a buffer of 0.1 seconds
)

# Check if intervals_to_remove is not empty or None
if not intervals_to_remove:
    print("No intervals to remove.")
else:
    # Step 6: Remove intervals from audio and video with smooth transitions
    remove_intervals_from_audio_video(
        video_path,
        intervals_to_remove,
        output_video_path
    )

print("Processing completed.")