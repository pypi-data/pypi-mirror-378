from .functions import *
from ..imports import *
from .info_utils import infoRegistry  # assumes your class is in a file like info_registry.py
# 🔹 NEW: for downloads
def derive_download_directory(video_directory=None):
    """Default downloads under <video_directory>/videos."""
    video_directory = video_directory or derive_video_directory()
    return os.path.join(video_directory, "videos")

def get_download_directory(download_directory=None, key=None, envPath=None):
    """Get or create the video download directory."""
    key = key or "VIDEO_DOWNLOAD_DIRECTORY"
    download_directory = (
        download_directory
        or get_env_value(key=key, path=envPath)
        or derive_download_directory()
    )
    os.makedirs(download_directory, exist_ok=True)
    return download_directory
class VideoDownloader:
    def __init__(self, url, title=None, download_directory=None,
                 user_agent=None, video_extention='mp4',
                 download_video=True, get_info=False, auto_file_gen=True,
                 standalone_download=False, output_filename=None, ydl_opts=None,
                 registry=None, force_refresh=False):

        self.url = url
        self.ydl_opts = ydl_opts or {}
        self.monitoring = True
        self.pause_event = threading.Event()
        self.get_download = download_video
        self.get_info = get_info
        self.user_agent = user_agent
        self.title = title
        self.auto_file_gen = auto_file_gen
        self.standalone_download = standalone_download
        self.video_extention = video_extention

        # 🔹 use derived download directory if not specified
        self.download_directory = get_download_directory(download_directory)
        
        self.output_filename = output_filename
        self.header = {}
        self.file_name, self.ext = os.path.splitext(os.path.basename(self.url))
        self.video_urls = url if isinstance(url, list) else [url]
        self.info = {}
        self.starttime = None
        self.downloaded = 0
        self.registry = registry or infoRegistry()
        self.force_refresh = force_refresh
        self.send_to_dl()
    def send_to_dl(self):
        if self.standalone_download:
            self.standalone_downloader()
        else:
            self.start()

    def get_headers(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.headers
        else:
            logger.error(f"Failed to retrieve headers for {url}. Status code: {response.status_code}")
            return {}

    @staticmethod
    def get_directory_path(directory, name, video_extention):
        file_path = os.path.join(directory, f"{name}.{video_extention}")
        i = 0
        while os.path.exists(file_path):
            file_path = os.path.join(directory, f"{name}_{i}.{video_extention}")
            i += 1
        return file_path

    def download(self):
        for video_url in self.video_urls:
            # 🔹 1. Try registry first
            cached_info = self.registry.get_video_info(video_url, force_refresh=self.force_refresh)
            if cached_info and not self.force_refresh:
                self.info = cached_info
                if "file_path" in cached_info and os.path.exists(cached_info["file_path"]):
                    logger.info(f"Serving cached video info for {video_url}")
                    self.stop()
                    return self.info

            # 🔹 2. Build output path
            if self.output_filename:
                outtmpl = os.path.join(self.download_directory, self.output_filename)
            else:
                temp_id = re.sub(r"[^\w\d.-]", "_", video_url)[-20:]
                outtmpl = os.path.join(self.download_directory, f"temp_{temp_id}.%(ext)s")

            ydl_opts = {
                'external_downloader': 'ffmpeg',
                'outtmpl': outtmpl,
                'noprogress': True,
                'quiet': True,
            }
            ydl_opts = {**ydl_opts, **self.ydl_opts}

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.info = ydl.extract_info(video_url, download=self.get_download)
                    self.starttime = get_time_stamp()
                    file_path = ydl.prepare_filename(self.info)

                    # 🔹 attach file_path into info
                    self.info['file_path'] = file_path

                    # 🔹 save/update registry
                    self.registry.get_video_info(video_url, video_id=self.info.get("id"), force_refresh=True)

                    # registry now points url → id → metadata (and file path)
                    cache_path = self.registry._get_cache_path(self.info["id"])
                    with open(cache_path, "w", encoding="utf-8") as f:
                        json.dump(self.info, f, indent=2)

                    if self.get_info:
                        self.stop()
                        return self.info
            except Exception as e:
                logger.error(f"Failed to download {video_url}: {str(e)}")

            self.stop()
        return self.info

    def monitor(self):
        while self.monitoring:
            logger.info("Monitoring...")
            self.pause_event.wait(60)
            if self.starttime:
                elapsed_time = subtract_it(get_time_stamp(), self.starttime)
                if self.downloaded != 0 and elapsed_time != 0:
                    cumulative_time = add_it(self.downloaded, elapsed_time)
                    percent = divide_it(self.downloaded, cumulative_time)
                else:
                    percent = 0
                if percent and elapsed_time:
                    try:
                        downloaded_minutes = divide_it(elapsed_time, 60)
                        estimated_download_minutes = divide_it(downloaded_minutes, percent)
                        estimated_download_time = subtract_it(estimated_download_minutes, downloaded_minutes)
                        if estimated_download_time >= 1.5:
                            logger.info("Restarting download due to slow speed...")
                            self.start()
                    except ZeroDivisionError:
                        logger.warning("Division by zero in monitor!")
                        continue

    def start(self):
        self.download_thread = threading.Thread(target=self.download)
        self.download_thread.daemon = True
        self.monitor_thread = threading.Thread(target=self.monitor)
        self.download_thread.start()
        self.monitor_thread.start()
        self.download_thread.join()
        self.monitor_thread.join()

    def stop(self):
        self.monitoring = False
        self.pause_event.set()
