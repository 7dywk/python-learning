import yt_dlp


video_url = "https://www.twitch.tv/evelone2004/clip/GleamingTriumphantPotNotLikeThis-XE7KMqXFtqK2Kp9R"
opts = {
    "format": 'best',
    "outtmpl": 'downloads_tt/%(title)s.%(ext)s',
}
with yt_dlp.YoutubeDL(opts) as ydl:
    result = ydl.download([video_url])
