from ..imports import *

class infoRegistry(metaclass=SingletonMeta):
    """Singleton for managing video + info registry directories."""

    def __init__(self, video_directory=None, envPath=None, info_directory=None):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.videoDirectory = get_video_directory(video_directory=video_directory, envPath=envPath)
            self.infoRegistryDirectory = get_info_directory(info_directory=info_directory, envPath=envPath)
            self.registry_path = os.path.join(self.infoRegistryDirectory, "registry.json")
            self._load_registry()

    def _load_registry(self):
        if os.path.isfile(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.registry = json.load(f)
        else:
            self.registry = {"by_url": {}, "by_id": {}}

    def _save_registry(self):
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2)

    def _get_cache_path(self, video_id):
        return os.path.join(self.infoRegistryDirectory, f"{video_id}.json")

    def get_video_info(self, url=None, video_id=None, force_refresh=False):
        if not (url or video_id):
            raise ValueError("Either url or video_id must be provided")

        # 1. Lookup video_id from registry if only URL given
        if url and not video_id:
            video_id = self.registry["by_url"].get(url)

        # 2. If video_id known, check cache
        if video_id:
            cache_path = self._get_cache_path(video_id)
            if os.path.isfile(cache_path) and not force_refresh:
                with open(cache_path, "r", encoding="utf-8") as f:
                    return json.load(f)

        # 3. Otherwise, fetch with yt_dlp
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        video_id = info.get("id") or hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        cache_path = self._get_cache_path(video_id)

        # Save to cache
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2)

        # Update registry
        if url:
            self.registry["by_url"][url] = video_id
        self.registry["by_id"][video_id] = {"url": url, "timestamp": time.time()}
        self._save_registry()

        return info

    def list_cached_videos(self):
        """Return all cached entries (url, id, metadata)."""
        results = []
        for vid, meta in self.registry["by_id"].items():
            results.append({"video_id": vid, "url": meta["url"], "timestamp": meta["timestamp"]})
        return results

def get_temp_id(url):
    url = str(url)
    url_length = len(url)
    len_neg = 20
    len_neg = len_neg if url_length >= len_neg else url_length
    temp_id = re.sub(r'[^\w\d.-]', '_', url)[-len_neg:]
    return temp_id
def get_temp_file_name(url):
    temp_id = get_temp_id(url)
    temp_filename = f"temp_{temp_id}.mp4"
    return temp_filename
def get_display_id(info):
    display_id = info.get('display_id') or info.get('id')
    return display_id
def get_video_title(info):
    title = info.get('title', 'video')[:30]
    return title
def get_safe_title(title):
    re_str = r'[^\w\d.-]'
    safe_title = re.sub(re_str, '_', title)
    return safe_title
def get_video_info_from_mgr(video_mgr):
    try:
        info = video_mgr.info
        return info
    except Exception as e:
        print(f"{e}")
        return None
def get_video_info(url, directory=None, output_filename=None,
                   get_info=None, download_video=None,
                   download_directory=None, ydl_opts=None):
    directory = directory or download_directory or os.getcwd()
    output_filename = output_filename or get_temp_file_name(url)
    get_info = bool_or_default(get_info)
    download_video = bool_or_default(download_video, default=False)
    return VideoDownloader(
        url=url,
        download_directory=directory,
        download_video=download_video,
        get_info=get_info,
        output_filename=output_filename,
        ydl_opts=ydl_opts,  # pass through
    )
