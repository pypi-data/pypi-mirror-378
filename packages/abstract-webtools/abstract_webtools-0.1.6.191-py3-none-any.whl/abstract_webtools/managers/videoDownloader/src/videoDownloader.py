from .functions import *
from .imports import *
class VideoDownloader:
    def __init__(self, url, title=None, download_directory=os.getcwd(), user_agent=None, video_extention='mp4', 
                 download_video=True, get_info=False, auto_file_gen=True, standalone_download=False, output_filename=None):
        self.url = url
        self.monitoring = True
        self.pause_event = threading.Event()
        self.get_download = download_video
        self.get_info = get_info
        self.user_agent = user_agent
        self.title = title
        self.auto_file_gen = auto_file_gen
        self.standalone_download = standalone_download
        self.video_extention = video_extention
        self.download_directory = download_directory
        self.output_filename = output_filename  # New parameter for custom filename
        self.header = {}  # Placeholder for UserAgentManagerSingleton if needed
        self.base_name = os.path.basename(self.url)
        self.file_name, self.ext = os.path.splitext(self.base_name)
        self.video_urls = [self.url]
        self.info = {}
        self.starttime = None
        self.downloaded = 0
        self.video_urls = url if isinstance(url, list) else [url]
        self.send_to_dl()

    def get_request(self, url):
        self.request_manager = requestManagerSingleton.get_instance(url=url)
        return self.request_manager

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

    def progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        self.downloaded = total_size - bytes_remaining

    def download(self):
        for video_url in self.video_urls:
            # Use custom filename if provided, otherwise generate a short temporary one
            if self.output_filename:
                outtmpl = os.path.join(self.download_directory, self.output_filename)
            else:
                temp_id = re.sub(r'[^\w\d.-]', '_', video_url)[-20:]  # Short temp ID from URL
                outtmpl = os.path.join(self.download_directory, f"temp_{temp_id}.%(ext)s")
            
            ydl_opts = {
                'external_downloader': 'ffmpeg',
                'outtmpl': outtmpl,
                'noprogress': True,
                'quiet': True,  # Reduce verbosity in logs
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.info = ydl.extract_info(video_url, download=self.get_download)
                    self.downloading = False
                    self.starttime = get_time_stamp()  # Assuming get_time_stamp() exists
                    if self.auto_file_gen:
                        file_path = ydl.prepare_filename(self.info)
                        if self.get_info:
                            self.info['file_path'] = file_path  # Fixed typo 'aath'
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
            self.pause_event.wait(60)  # Check every minute
            if self.starttime:
                elapsed_time = subtract_it(get_time_stamp(),self.starttime)
                if self.downloaded != 0 and elapsed_time != 0:
                    cumulative_time = add_it(self.downloaded,elapsed_time)
                    percent = divide_it(self.downloaded,cumulative_time)
                else:
                    percent = 0
                if elapsed_time != 0:
                    try:
                        downloaded_minutes = divide_it(elapsed_time,60)
                        estimated_download_minutes = divide_it(downloaded_minutes,percent)
                        estimated_download_time =  subtract_it(estimated_download_minutes,downloaded_minutes)
                    except ZeroDivisionError:
                        logger.warning("Caught a division by zero in monitor!")
                        continue
                if downloaded_minutes != 0 and subtract_it(percent,downloaded_minutes) != 0:
                    estimated_download_minutes = divide_it(downloaded_minutes,percent)
                    estimated_download_time =  subtract_it(estimated_download_minutes,downloaded_minutes)
                    logger.info(f"Estimated download time: {estimated_download_time} minutes")
                if estimated_download_time >= 1.5:
                    logger.info("Restarting download due to slow speed...")
                    self.start()  # Restart download

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
