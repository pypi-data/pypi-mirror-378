from .functions import *
from ..imports import *
from .info_utils import infoRegistry  # assumes your class is in a file like info_registry.py

class VideoDownloader:
    def __init__(self, url, title=None, download_directory=None,
                 data_directory=None,temp_directory=None,
                 user_agent=None, video_extention='mp4',
                 download_video=True, get_info=False, auto_file_gen=True,
                 standalone_download=False, output_filename=None, ydl_opts=None,
                 registry=None, force_refresh=False):
        self.url = get_corrected_url(url=url)
        self.registry = registry or infoRegistry()
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
        self.download_directory = get_download_directory(download_directory)
        self.tempDirectory = get_temp_directory(directory=temp_directory)
        self.dataDirectory = get_data_directory(directory=data_directory)
        self.output_filename = output_filename  # New parameter for custom filename
        self.header = {}  # Placeholder for UserAgentManagerSingleton if needed
        self.base_name = os.path.basename(self.url)
        self.file_name, self.ext = os.path.splitext(self.base_name)
        self.video_urls = [self.url]
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
        req_mgr = requestManager(url)
        if req_mgr.status_code == 200:
            return req_mgr.response.headers
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
            logger.info(f"[VideoDownloader] Starting process for: {video_url}")

            # 🔹 1. Try registry first
            cached_info = self.registry.get_video_info(video_url, force_refresh=self.force_refresh)
            file_already_downloaded = False

            if cached_info:
                self.info = cached_info
                logger.info(f"[VideoDownloader] Found cached info for {video_url}: {cached_info.get('id')}")
                file_path = cached_info.get("file_path")

                if file_path and os.path.isfile(file_path):
                    logger.info(f"[VideoDownloader] Found existing file at {file_path}")
                    file_already_downloaded = True

            # 🔹 2. Decide whether to skip download
            if file_already_downloaded:
                if not self.force_refresh and not self.get_download:
                    logger.info(f"[VideoDownloader] Skipping download (file exists and no refresh needed).")
                    self.stop()
                    return self.info
                elif not self.get_download:
                    logger.info(f"[VideoDownloader] get_download=False; skipping actual download.")
                    self.stop()
                    return self.info

            # 🔹 3. Prepare yt-dlp options and run download
            if self.get_download:
                # -- temp dir output path
                outtmpl = os.path.join(self.tempDirectory, self.output_filename) if self.output_filename else os.path.join(self.tempDirectory, "%(id)s.%(ext)s")
                logger.info(f"[VideoDownloader] Output template: {outtmpl}")

                ydl_opts = self.build_ydl_opts()
                ydl_opts = {**ydl_opts, "outtmpl": outtmpl}
                logger.debug(f"[VideoDownloader] yt-dlp options: {ydl_opts}")

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        self.info = ydl.extract_info(video_url, download=True)
                        self.starttime = get_time_stamp()

                        video_id = self.info.get("id")
                        temp_path = ydl.prepare_filename(self.info)

                        basename = os.path.basename(temp_path)
                        filename, ext = os.path.splitext(basename)
                        dirbase = os.path.join(self.download_directory, filename)
                        final_path = os.path.join(dirbase, f"video{ext}")

                        if temp_path != final_path:
                            try:
                                os.makedirs(dirbase, exist_ok=True)
                                shutil.move(temp_path, final_path)
                                logger.info(f"[VideoDownloader] Moved file to: {final_path}")
                                self.info["file_path"] = final_path
                            except Exception as e:
                                logger.error(f"[VideoDownloader] Failed to move file: {e}")
                                self.info["file_path"] = temp_path
                        else:
                            self.info["file_path"] = temp_path

                        self.info["video_id"] = video_id
                        cache_path = self.registry._get_cache_path(video_id)
                        self.info = self.registry.edit_info(data=self.info, url=video_url, video_id=video_id)
                        logger.info(f"[VideoDownloader] Saved info to registry: {cache_path}")

                        if self.get_info:
                            self.stop()
                            return self.info

                except Exception as e:
                    logger.error(f"[VideoDownloader] Failed to download {video_url}: {str(e)}")

            else:
                logger.info("[VideoDownloader] get_download is False; skipping actual download.")

            self.stop()
        return self.info

    def build_ydl_opts(self):
        # Start with base options
        ydl_opts = {
            'quiet': True,
            'noprogress': True,
            'external_downloader': 'ffmpeg',
        }

        # Set output path template
        if self.output_filename:
            ydl_opts['outtmpl'] = os.path.join(self.tempDirectory, self.output_filename)
        else:
            ydl_opts['outtmpl'] = os.path.join(self.tempDirectory, '%(id)s.%(ext)s')

        # Optional: enforce mp4 extension format if requested
        if self.video_extention and self.video_extention != 'mp4':
            ydl_opts['format'] = f"bestvideo[ext={self.video_extention}]+bestaudio[ext=m4a]/best[ext={self.video_extention}]"
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'

        # Apply user-agent if present
        if self.user_agent:
            ydl_opts['http_headers'] = {
                'User-Agent': self.user_agent
            }

        # Merge with externally provided overrides
        ydl_opts.update(self.ydl_opts)

        return ydl_opts


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
