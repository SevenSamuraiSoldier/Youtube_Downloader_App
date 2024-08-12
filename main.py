import streamlit as st
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import ffmpeg

# Streamlit app title
st.title("YouTube Downloader")

# Prompt the user to enter the YouTube video URL
url = st.text_input("Enter the YouTube video URL:")

def repeat_word_check(title ,resolution, fps, outputExt):
    # Convert the words and string to lowercase
    resolution_lower = resolution.lower()
    fps_lower = (str(fps) + "fps").lower()
    string_lower = title.lower()
    
    # Check for the presence of both words
    found_resolution = resolution_lower in string_lower
    found_fps = fps_lower in string_lower

    # Determine the output based on the findings
    if found_resolution and found_fps:
        return f"{title}{outputExt}"
    elif found_resolution:
        return f"{title}_{fps}fps{outputExt}"
    elif found_fps:
        return f"{title}_{resolution}{outputExt}"
    else:
        return f"{title}_{resolution}_{fps}fps{outputExt}"
    

#------Main Logic Start Here!!!-----#/////////////////////////////////////////
if url:
    # Create a YouTube object with the provided URL and a progress callback
    yt = YouTube(url, on_progress_callback=on_progress)

    # Display the title of the video
    st.write(f"Downloading from: **{yt.title}**")

    # Allow user to select audio or video+audio
    download_type = st.selectbox("Select download type:", ["Audios", "Videos", "Only Videos", "All"])

    # Get the available streams based on the selected download type
    if download_type == "Audios":
        streams = yt.streams.filter(only_audio=True)
    elif download_type == "Videos":
        streams = yt.streams.filter(progressive=True)
    elif download_type == "Only Videos":
        streams = yt.streams.filter(adaptive=True)
    else:
        streams = yt.streams

    # Display the available streams with assigned numbers
    st.write("Available streams:")
    stream_options = {
        f"itag: {stream.itag}, res: {stream.resolution}, abr: {stream.abr}, mime_type: {stream.mime_type}, fps: {stream.fps if hasattr(stream, 'fps') else 'N/A'}": stream 
        for stream in streams
    }
    selected_stream = st.selectbox("Select a stream:", list(stream_options.keys()))

    # Confirm download
    if st.button("Download Selected Stream"):
        stream = stream_options[selected_stream]
        st.write(f"Selected stream: itag {stream.itag}, {stream.resolution}, {stream.abr}, mime_type: {stream.mime_type}, fps: {stream.fps if hasattr(stream, 'fps') else 'N/A'}")

        
        filename_audio = ""
        # Determine the file extension
        if stream.mime_type.startswith('video'):
            file_extension = '.mp4'  # Assuming video files are in mp4 format
            filename = f"{yt.title}_video{file_extension}"
            if download_type == "Only Videos":
                audio_stream = yt.streams.get_by_itag(251)
                audio_extension = '.mp3'
                filename_audio = f"{yt.title}_audio{audio_extension}"
        else:
            file_extension = '.mp3'  # Assuming audio files are in mp3 format
            filename = f"{yt.title}_audio{file_extension}"

        # Download the selected stream
        st.write("Downloading...")
        stream.download(filename=filename)
        st.success("Video Download completed!")


        #---Code BLock to download Audio for Video only streams & combine the two---------
        if filename_audio != "":
            st.write("Downloading Audio for the Video File....")
            audio_stream.download(filename=filename_audio)
            st.success("Audio Download Completed!...")
            # Merging audio and video into output.mkv
            outputFileExtension = '.mkv'
            #outputFilename = f"{yt.title}_{stream.resolution}_{stream.fps}fps{outputFileExtension}"
            outputFilename = repeat_word_check(yt.title,stream.resolution, stream.fps, outputFileExtension)
            st.write("Merging audio and video into output.mkv...")
            os.system(f'ffmpeg -i "{filename}" -i "{filename_audio}" -c:v copy -c:a copy "{outputFilename}"')
            st.success(f'Merging completed! The output file is {outputFilename}')
            filename_audio = ""

            #os.system(f'ffmpeg -i "{filename}" -i "{filename_audio}" -c:v copy -c:a copy "output.mp4"')




