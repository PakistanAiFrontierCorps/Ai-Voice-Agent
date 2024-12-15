import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import datetime,os,time,random,json,requests
from pathlib import Path

def get_most_recent_video(folder_path):
    files = Path(folder_path).glob("*")
    video_extensions = [".mp4", ".avi", ".mov", ".mkv"]
    video_files = [file for file in files if file.suffix.lower() in video_extensions]
    video_files = sorted(video_files, key=os.path.getmtime, reverse=True)
    return video_files[0] if video_files else None

def save_audio_file(audio_bytes, file_extension):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"audio_{timestamp}.{file_extension}"

    with open(file_name, "wb") as f:
        f.write(audio_bytes)

    return file_name

def transcribe_to_text(file_path):
    text = None
    with open(file_path, "rb") as audio_file:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
    return text

import chromadb
chroma_client = chromadb.Client()
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
collection = chroma_client.create_collection(name=f"my_collection_{timestamp}")
collection.add(
    documents=[
        "My name is Shahbaz Ali.",
        "I am studying Computer Science",
        "I am a student in the University of the Punjab",
        "I have applied to Timerni for Internship.",
        "I am expecting a good career start at Timerni"
    ],
    ids=["id1", "id2","id3","id4","id5"]
) 
def query_answer(query):
  results = collection.query(
      query_texts=[query],
      n_results=1
  )
  if results['distances']:
      least_distance_index = results['distances'].index(min(results['distances']))
      most_relevant_document = results['documents'][least_distance_index][0]
      return most_relevant_document
  else:
      print("No matching results found.")


def main():
    st.title("Audio to Text using AI")
    audio_bytes = audio_recorder()
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        save_audio_file(audio_bytes, "mp3")

    if st.button("Get Response"):

        audio_file_path = max(
            [f for f in os.listdir(".") if f.startswith("audio")],
            key=os.path.getctime,
        )

        transcript_text = transcribe_to_text(audio_file_path)
        answer_to_query = query_answer(transcript_text)

        st.header("Answer")
        st.write(answer_to_query)
        with open("transcript.txt", "w") as f:
            f.write(transcript_text)
        # st.download_button("Download Transcript", transcript_text)
        ##############################################
        
        url = "https://api.d-id.com/talks"
        api_key = "bmFnaWtpYjIwMUBsb2ZpZXkuY29t:BZK3VWg8-Ks34EDpyV9pz"
        payload = json.dumps({
        "script": {
            "type": "text",
            "input": answer_to_query,
            "provider": {
            "type": "microsoft",
            "voice id": "en-US-DavisNeural",
            "voice config": {
                " style": "Cheerful "
            }
            }
        },
        "cofig": {
            "stitch": "true"
        },
        "source url": "https://create-images-results.d-id.com/gooele-oauth2%7C103965831765131871486/drm_tgSnNQLNmB-R050vQi_Q7/image.png",
        "webhook": "https://host.domain.tld/to/webhook"
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {api_key}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # st.write(response.text)
        response_json = response.json()
        value = response_json.get("id")
        url = f"https://api.d-id.com/talks/{value}"
        payload = {}
        headers = {
        'Authorization': f'Basic {api_key}'
        }
        time.sleep(10)
        response = requests.request("GET", url, headers=headers, data=payload)
        # st.write(response.text)
        response_json = response.json()
        value = response_json.get("result_url")
        # cleaned_value = value.strip("'")
        st.write("Your Result URL is Below")
        st.write(value)
        if st.button("Get Your Answer"):
            st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)
        time.sleep(7)
        video_folder = r"C:\Users\Shahbaz\Downloads"
        recent_video = get_most_recent_video(video_folder)
        if recent_video:
            st.write(f"Playing: {recent_video.name}")
            st.video(str(recent_video))
        else:
            st.write("No videos found in the specified folder.")

if __name__ == "__main__":
    main()