from kokoro import KPipeline
import soundfile as sf
import simpleaudio as sa
import customtkinter
import threading
import os
from pathlib import Path
import librosa
import pyrubberband
import numpy as np

audio_folder = Path('audio_files')
playing = False
cur_text = []
stop_event = threading.Event()
end_event = threading.Event()
writing_event = threading.Event()
playing_event = threading.Event()

voices = [
    'af_heart',
    'af_alloy',
    'af_aoede',
    'af_bella',
    'af_jessica',
    'af_kore',
    'af_nicole',
    'af_nova',
    'af_river',
    'af_sarah',
    'af_sky',
    'am_adam',
    'am_echo',
    'am_eric',
    'am_fenrir',
    'am_liam',
    'am_michael',
    'am_onyx',
    'am_puck',
    'am_santa'
]

def button_callback(textbox, label, voice, speed):
    def play_text():
        # ensure no duplicate playing
        if playing_event.is_set():
            return
        else:
            playing_event.set()
        # play audio
        clear_folder()
        text = textbox.get("0.0", "end")
        thread = threading.Thread(target=narrate_wrapper(text, label, voice, speed))
        thread.start()
    return play_text

def play_thread_wrapper(label, speed):
    def play_thread():
        i = 0
        while True:
            if stop_event.is_set():
                return
            audio_path = audio_folder / f'{i}.wav'
            while not os.path.exists(audio_path):
                if end_event.is_set():
                    reset_events()
                    return
            while writing_event.is_set():
                pass
            y, sr = librosa.load(audio_path, sr=None)
            try:
                y_fast = pyrubberband.pyrb.time_stretch(y, sr, rate=speed.get())
            except RuntimeError:
                # if pyrubberband not installed
                y_fast = librosa.effects.time_stretch(y, rate=speed.get())
            y_fast = y_fast / np.max(np.abs(y_fast))
            audio_int16 = (y_fast * 32767).astype(np.int16)
            audio_bytes = audio_int16.tobytes()
            play_obj = sa.play_buffer(audio_bytes, 1, 2, sr)
            label.configure(text=f'text {i}: {cur_text[i]}')
            play_obj.wait_done()
            i += 1
    return play_thread

def narrate_wrapper(text, label, voice, speed):
    def narrate():
        pipeline = KPipeline(lang_code='a')
        generator = pipeline(text, voice=voice.get())
        cur_play_thread = threading.Thread(target=play_thread_wrapper(label, speed))
        cur_play_thread.start()
        for i, (gs, ps, audio) in enumerate(generator):
            writing_event.set()
            sf.write(f'audio_files/{i}.wav', audio, 24000)
            writing_event.clear()
            cur_text.append(gs)
            if stop_event.is_set():
                return
        end_event.set()
    return narrate

def reset_events():
    playing_event.clear()
    stop_event.clear()
    end_event.clear()

def stop_playback():
    stop_event.set()
    playing_event.clear()

def update_slider_label(label):
    def update_label(value):
        label.configure(text=f'Current Speed: {value:.2f}')
    return update_label

def clear_folder():
    for file in audio_folder.iterdir():
        if file.is_file():
            file.unlink()

def main():
    audio_folder.mkdir(parents=True, exist_ok=True)

    app = customtkinter.CTk()
    app.title("my app")
    app.geometry("400x800")

    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    label = customtkinter.CTkLabel(app, text="Voice:", fg_color="transparent")
    label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
    optionmenu_var = customtkinter.StringVar(value="af_heart")
    optionmenu = customtkinter.CTkOptionMenu(app,values=voices,
                                            variable=optionmenu_var)
    optionmenu.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
    label = customtkinter.CTkLabel(app, text="Current Speed: 1", fg_color="transparent")
    label.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
    slider_var = customtkinter.DoubleVar(value=1)
    slider = customtkinter.CTkSlider(app, from_=0.25, to=4, variable=slider_var, command=update_slider_label(label))
    slider.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
    label = customtkinter.CTkLabel(app, text="Text to narrate:", fg_color="transparent")
    label.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
    textbox = customtkinter.CTkTextbox(app)
    textbox.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
    label = customtkinter.CTkLabel(app, text="Current text will show here", fg_color="transparent", wraplength=360, justify="left")
    label.grid(row=8, column=0, padx=20, pady=20, sticky="ew")
    button = customtkinter.CTkButton(app, text="Play", command=button_callback(textbox, label, optionmenu_var, slider_var))
    button.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
    button = customtkinter.CTkButton(app, text="Stop", command=stop_playback)
    button.grid(row=7, column=0, padx=20, pady=20, sticky="ew")

    app.mainloop()
        
if __name__ == '__main__':
    main()