import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip

# Вказуй шлях до свого завантаженого відео
video = VideoFileClip("downloads_tt/f.mp4")

# Беремо один кадр на 10-й секунді відео (щоб стрімер точно був у кадрі)
frame = video.get_frame(5)

# Показуємо цей кадр як картинку
plt.imshow(frame)
plt.show()