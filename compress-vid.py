import ffmpeg
import os
import shutil

def compress_video(folder="target-vid", target_size_mb=5):
    """
    Compresses the only video in the target folder and overwrites the file.

    :param folder: The folder containing the video file.
    :param target_size_mb: Target size of the output video in megabytes.
    """
    try:
        # Ensure the folder exists
        if not os.path.exists(folder):
            raise FileNotFoundError(f"The folder '{folder}' does not exist.")

        # Get the only video file in the folder
        video_files = [
            f for f in os.listdir(folder)
            if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))
        ]
        if len(video_files) != 1:
            raise ValueError(f"The folder '{folder}' must contain exactly one video file.")

        input_file = os.path.join(folder, video_files[0])
        temp_output_file = os.path.join(folder, 'temp_compressed_video.mp4')

        # Get video metadata
        probe = ffmpeg.probe(input_file)
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None
        )
        if video_stream is None:
            raise ValueError("No video stream found in the input file.")

        duration = float(probe['format']['duration'])

        # Calculate target bitrate in bits per second and convert to kilobits per second
        target_bitrate = (target_size_mb * 8 * 1024 * 1024) / duration  # bits per second
        target_bitrate_kbps = int(target_bitrate / 1000)  # kilobits per second

        print(f"Target bitrate: {target_bitrate_kbps} kbps")

        # Set minimum and maximum bitrate thresholds to prevent quality degradation
        min_bitrate_kbps = 300  # Minimum acceptable video bitrate in kbps
        max_bitrate_kbps = 5000  # Maximum acceptable video bitrate in kbps

        if target_bitrate_kbps < min_bitrate_kbps:
            print(f"Calculated bitrate is too low; setting to minimum bitrate: {min_bitrate_kbps} kbps")
            target_bitrate_kbps = min_bitrate_kbps
        elif target_bitrate_kbps > max_bitrate_kbps:
            print(f"Calculated bitrate is too high; setting to maximum bitrate: {max_bitrate_kbps} kbps")
            target_bitrate_kbps = max_bitrate_kbps

        # Compress the video using FFmpeg
        (
            ffmpeg
            .input(input_file)
            .output(
                temp_output_file,
                **{
                    'c:v': 'libx264',
                    'b:v': f'{target_bitrate_kbps}k',
                    'pass': 1,
                    'c:a': 'aac',
                    'b:a': '128k',
                    'movflags': '+faststart',
                    'preset': 'slow',
                }
            )
            .overwrite_output()
            .run()
        )

        # Replace the original file with the compressed file
        os.remove(input_file)
        shutil.move(temp_output_file, input_file)

        # Verify compression
        compressed_size_mb = os.path.getsize(input_file) / (1024 * 1024)
        print(f"Compression complete. Final size: {compressed_size_mb:.2f} MB. Updated file: {input_file}")

    except ffmpeg.Error as e:
        print(f"An FFmpeg error occurred: {e.stderr.decode()}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the script
if __name__ == "__main__":
    folder_name = "target-vid"
    target_size = 5  # Set target size in MB
    compress_video(folder=folder_name, target_size_mb=target_size)
