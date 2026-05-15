import os
import yt_dlp
from moviepy.editor import VideoFileClip, clips_array

# 1. ЗАПИТУЄМО ПОСИЛАННЯ (тепер не треба міняти код щоразу)
video_url = input("Встав посилання на кліп Twitch сюди і натисни Enter: ")

print("\n[КРОК 1] Починаю завантаження кліпу...")

opts = {
    "format": 'best',
    "outtmpl": 'downloads_tt/%(title)s.%(ext)s',
}

# 2. ЗАВАНТАЖУЄМО І ДІЗНАЄМОСЯ ТОЧНУ НАЗВУ ФАЙЛУ
with yt_dlp.YoutubeDL(opts) as ydl:
    # extract_info качає відео і повертає нам словник з усіма даними (назва, автор, тривалість)
    info_dict = ydl.extract_info(video_url, download=True)
    # Ця команда магічним чином генерує точний шлях до збереженого файлу
    downloaded_file_path = ydl.prepare_filename(info_dict)

print(f"\n[КРОК 2] Кліп успішно завантажено: {downloaded_file_path}")
print("Починаю нарізку та монтаж...")

# 3. ПЕРЕДАЄМО ФАЙЛ У МОНТАЖЕР (тепер назва динамічна, а не жорстко прописана)
video = VideoFileClip(downloaded_file_path)

from moviepy.editor import clips_array

# 1. Основний контент (верхній великий екран)
gameplay = video.crop(x1=420, y1=0, x2=2140, y2=960).resize(width=1080)

# 2. Головний стрімер (по центру)
main_webcam = video.crop(x1=910, y1=1010, x2=1700, y2=1440).resize(width=1080)

# 3. Лівий стрімер
# Беремо координати зліва від центральної вебки
left_webcam = video.crop(x1=100, y1=1010, x2=890, y2=1440)
left_webcam = left_webcam.resize(width=540) # Робимо ширину рівно на пів екрана

# 4. Правий стрімер
# Беремо координати справа від центральної вебки
right_webcam = video.crop(x1=1720, y1=1010, x2=2510, y2=1440)
right_webcam = right_webcam.resize(width=540) # Теж на пів екрана

# 5. МАГІЯ ЗБИРАННЯ
# Спочатку зліплюємо лівого і правого стрімера в один горизонтальний ряд
bottom_row = clips_array([[left_webcam, right_webcam]])

# Тепер збираємо фінальне відео: Гра зверху, головний по центру, інші двоє знизу
final_clip = clips_array([
    [main_webcam],
    [gameplay],
    [bottom_row]
])

# 4. ГЕНЕРУЄМО НАЗВУ ДЛЯ ТІКТОКУ ТА РЕНДЕРИМО
# Беремо оригінальну назву і додаємо "_tiktok", щоб файли не переплутались
base_name = os.path.basename(downloaded_file_path)
name_without_ext = os.path.splitext(base_name)[0]
output_path = f"downloads_tt/{name_without_ext}_tiktok.mp4"

print("\n[КРОК 3] Починаю фінальний рендер. Можна йти пити чай!")
final_clip.write_videofile(
    output_path,
    codec="libx264",
    audio_codec="aac",
    fps=60,
    threads=4,
    preset="fast"
)

print(f"\n✅ ГОТОВО! Твоє відео для ТікТоку збережено тут: {output_path}")

# За бажанням: можна розкоментувати наступний рядок, щоб скрипт сам видаляв
# оригінальне горизонтальне відео з Твіча після створення ТікТоку (економить місце на Маці)
os.remove(downloaded_file_path)