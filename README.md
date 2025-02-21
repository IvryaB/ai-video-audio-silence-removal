# AI Video and Audio Silence Removal

## Description

This script uses the **Whisper** model for speech recognition and removes pauses and filler words from audio and video files. The script automatically analyzes the audio, detects pauses, removes them, and then generates a processed video with smooth transitions between the remaining segments.

## Installation and Usage

### Step 1: Install Dependencies

Before starting, ensure that you have Python 3.6+ installed and run the following command to install the required libraries:

```bash
pip install moviepy pydub whisper
```

### Step 2: Downloading the Whisper Model

The Whisper model will be automatically downloaded on the first run of the script. The model weights are stored online, and an internet connection is required for the download.

### Step 3: Running the Script

1. **Prepare the video file** – Make sure you have a video file in `.mp4` format from which you want to extract the audio.

2. **Adjust parameters**:
   You can configure the settings for pause detection and silence threshold in the **detect_silences()** function, as well as the Whisper model and device in **transcribe_audio_with_whisper()**.

3. **Run the script**:
   After configuring the parameters and file paths, simply execute the script:

   ```bash
   python script_name.py
   ```

4. **Output**:
   The result will be a video file without pauses and filler words, saved as **output_video.mp4**.

## Configuration Parameters

- **min_silence_len** — Minimum length of a pause to be detected, in milliseconds. Default is 1000 (1 second).
- **silence_thresh** — Silence threshold in decibels. Default is -50.
- **model_name** — The Whisper model to use. Possible values: **base**, **small**, **medium**, **large**.
- **device** — The device for running the Whisper model. Possible values: **cuda** (for GPU) or **cpu**.

## How the Script Works

1. **Extracting audio** from the video using the **moviepy** library.
2. **Processing audio** using **pydub** to detect pauses and filler words.
3. **Speech recognition** with the **Whisper** model for transcription and filler word detection.
4. **Removing pauses and filler words** from the video using **moviepy**, ensuring smooth transitions between segments.

## Notes

- For more accurate results, you can select a more powerful Whisper model, but it will require more computational resources.
- Processing time may be significant for videos with long durations or high resolutions.
- If your video contains many pauses or filler words, the script may take longer to analyze and process.

## License

This project is distributed under the MIT license. See the LICENSE file for details.
