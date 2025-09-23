from .functions import *
from ..imports import *
from .info_utils import infoRegistry

class VideoDownloader:
    def __init__(self, url, download_directory=None, user_agent=None,
                 video_extention="mp4", download_video=True,
                 get_info=False, output_filename=None,
                 ydl_opts=None, registry=None, force_refresh=False):

        self.url = get_corrected_url(url=url)
        self.registry = registry or infoRegistry()
        self.ydl_opts = ydl_opts or {}
        self.get_download = download_video
        self.get_info = get_info
        self.user_agent = user_agent
        self.video_extention = video_extention
        self.download_directory = get_download_directory(download_directory)
        self.output_filename = output_filename
        self.force_refresh = force_refresh
        self.info = {}
        self.video_urls = [self.url]

        self.send_to_dl()

    def send_to_dl(self):
        self.start()

    def build_ydl_opts(self, outtmpl):
        ydl_opts = {
            "quiet": True,
            "noprogress": True,
            "external_downloader": "ffmpeg",
            "outtmpl": outtmpl,
        }
        if self.video_extention and self.video_extention != "mp4":
            ydl_opts["format"] = (
                f"bestvideo[ext={self.video_extention}]+bestaudio[ext=m4a]/best[ext={self.video_extention}]"
            )
        else:
            ydl_opts["format"] = "bestvideo+bestaudio/best"

        if self.user_agent:
            ydl_opts["http_headers"] = {"User-Agent": self.user_agent}

        ydl_opts.update(self.ydl_opts)
        return ydl_opts

    def download(self):
        for video_url in self.video_urls:
            logger.info(f"[VideoDownloader] Processing: {video_url}")

            # 🔹 Step 1: Check registry
            cached_info = self.registry.get_video_info(video_url, force_refresh=self.force_refresh)
            if cached_info and cached_info.get("file_path") and os.path.isfile(cached_info["file_path"]):
                logger.info(f"[VideoDownloader] Found cached file: {cached_info['file_path']}")
                return cached_info

            # 🔹 Step 2: Prepare yt-dlp options
            tmp_outtmpl = os.path.join(self.download_directory, "%(id)s.%(ext)s")
            ydl_opts = self.build_ydl_opts(tmp_outtmpl)

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=self.get_download)
                    video_id = info.get("id")
                    temp_path = ydl.prepare_filename(info)
                    basename = os.path.basename(temp_path)
                    _, ext = os.path.splitext(basename)

                    # 🔹 Step 3: Definitive dir layout
                    dirbase = os.path.join(self.download_directory, video_id)
                    os.makedirs(dirbase, exist_ok=True)
                    final_path = os.path.join(dirbase, f"video{ext}")

                    if temp_path != final_path:
                        shutil.move(temp_path, final_path)

                    # 🔹 Step 4: Save canonical info.json
                    info["file_path"] = final_path
                    info["video_id"] = video_id
                    info_path = os.path.join(dirbase, "info.json")
                    safe_dump_to_file(info, info_path)
                    info["info_path"] = info_path

                    # 🔹 Step 5: Update registry index
                    self.registry.edit_info(
                        data={"file_path": final_path, "info_path": info_path},
                        url=video_url,
                        video_id=video_id
                    )

                    logger.info(f"[VideoDownloader] Downloaded and stored at {final_path}")
                    self.info = info
                    return info

            except Exception as e:
                logger.error(f"[VideoDownloader] Download failed: {e}")
                return None




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
