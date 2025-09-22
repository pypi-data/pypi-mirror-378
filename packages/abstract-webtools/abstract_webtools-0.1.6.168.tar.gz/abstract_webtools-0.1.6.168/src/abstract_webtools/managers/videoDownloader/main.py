from src import *
reg = infoRegistry()

# First call → fetches with yt_dlp and caches
dl = VideoDownloader("https://www.youtube.com/watch?v=t-knFuqQdGc&list=RDt-knFuqQdGc&start_radio=1", get_info=True)

print(dl.info["file_path"])  # absolute path to downloaded video
print(dl.registry.list_cached_videos())  # show everything cached
