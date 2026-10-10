from moviepy.editor import VideoFileClip, clips_array

video = VideoFileClip("downloads_tt/f.mp4")

webcam = video.crop(x1=910, y1=1010, x2=1700, y2=1440)
webcam = webcam.resize(width=1080)

# 2. Вирізаємо основний контент (верхній великий чорний екран)
# По X він від 420 до 2140, по Y від самого верху (0) до 960
gameplay = video.crop(x1=420, y1=0, x2=2140, y2=960)
gameplay = gameplay.resize(width=1080)

final_clip = clips_array([[webcam], [gameplay]])

# Ось цього не вистачало! Команда зберегти фінальний результат:
print("Починаю рендер...")
final_clip.write_videofile(
    "downloads_tt/f.mp4",
    codec="libx264",
    audio_codec="aac",
    fps=60,
    threads=4,
    preset="fast"
)
print("Готово!")