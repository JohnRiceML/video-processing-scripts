from moviepy.editor import VideoFileClip
import os
import shutil

def trim_video(folder="target-vid", cut_duration=5):
    """
    Trims the first `cut_duration` seconds from the only video in the target folder.

    :param folder: The folder containing the video file.
    :param cut_duration: Number of seconds to trim from the start of the video.
    """
    try:
        # Ensure the folder exists
        if not os.path.exists(folder):
            raise FileNotFoundError(f"The folder '{folder}' does not exist.")

        # Get the only video file in the folder
        video_files = [f for f in os.listdir(folder) if f.endswith(('.mp4', '.mov', '.avi', '.mkv'))]
        if len(video_files) != 1:
            raise ValueError(f"The folder '{folder}' must contain exactly one video file.")

        input_file = os.path.join(folder, video_files[0])
        temp_output_file = os.path.join(folder, 'temp_trimmed_video.mp4')

        # Load the video file
        video = VideoFileClip(input_file)

        # Validate cut_duration
        if cut_duration >= video.duration:
            raise ValueError(f"The cut duration ({cut_duration}s) exceeds or matches the video length ({video.duration:.2f}s).")

        # Trim the video
        print(f"Trimming the first {cut_duration} seconds from '{input_file}'...")
        trimmed_video = video.subclip(cut_duration, video.duration)

        # Write the output to a temporary file
        trimmed_video.write_videofile(
            temp_output_file,
            codec="libx264",
            audio_codec="aac",
            ffmpeg_params=["-movflags", "faststart"]
        )

        # Close video clips to release file handles
        trimmed_video.close()
        video.close()

        # Replace the original file with the temporary file
        os.remove(input_file)
        shutil.move(temp_output_file, input_file)

        print(f"Video trimmed successfully. Updated file: {input_file}")

    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
    except ValueError as ve:
        print(f"Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Run the script
if __name__ == "__main__":
    folder_name = "target-vid"
    cut_duration = 5  # Set the number of seconds to trim
    trim_video(folder=folder_name, cut_duration=cut_duration)
