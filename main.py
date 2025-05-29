import pystray, keyboard, threading,time
import spotipy_spotify
from PIL import Image

def close_aplication(ikona_obj, item):
    print("Closing aplication...")
    ikona_obj.stop()

def action_after_hotkey_clicked():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{timestamp}] HOTKEY PRESSED! Launching...")
    spotipy_spotify.speech_search_spotify()

def hotkey_handling():
    print("Hotkey press detected. Starting action in a separate thread...")
    action = threading.Thread(target=action_after_hotkey_clicked, daemon=True)
    action.start()

def main():
    icon_file_name = "spotipy_icon.png"
    png_file = Image.open(icon_file_name)

    icon = pystray.Icon(
    'test name',
    icon=png_file)
    icon.menu = pystray.Menu(
        pystray.MenuItem('Close', close_aplication))

    keyboard.add_hotkey('ctrl+shift+m', hotkey_handling)

    icon.run()    


if __name__ == "__main__":
    main()



