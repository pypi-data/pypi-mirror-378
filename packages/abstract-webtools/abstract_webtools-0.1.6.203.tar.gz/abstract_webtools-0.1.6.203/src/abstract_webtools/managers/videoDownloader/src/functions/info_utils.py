from .functions import *
from ..imports import *
from abstract_utilities import get_any_value,make_list,safe_read_from_json


def get_video_info(url, ydl_opts=None,output_filename=None, cookies_path=None):
    from yt_dlp import YoutubeDL

    
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
    }

    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        print(f"Failed to extract video info: {e}")
        return None
class infoRegistry(metaclass=SingletonMeta):
    """Singleton for managing video + info registry directories."""

    def __init__(self, video_directory=None, envPath=None, info_directory=None,temp_directory=None,data_directory=None,**kwargs):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.videoDirectory = get_video_directory(video_directory=video_directory, envPath=envPath)
            self.infoRegistryDirectory = get_info_directory(directory=info_directory, envPath=envPath)
            self.tempDirectory = get_info_directory(directory=temp_directory, envPath=envPath)
            self.dataDirectory = get_info_directory(directory=data_directory, envPath=envPath)
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

    def _get_cache_path(self, video_id=None,url=None):
        video_id = self._get_video_id(url=url,video_id=video_id)
        return os.path.join(self.infoRegistryDirectory, f"{video_id}.json")

    def _get_video_id(self,url=None,video_id=None):
        if url and not video_id:
            video_id = self.registry["by_url"].get(url)
        return video_id
    def _fetch_get_id(self,url=None):
        ydl_opts = {"quiet": True, "skip_download": True}
        info = get_video_info(url,ydl_opts=ydl_opts)
        video_id = info.get("id") or hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        cache_path = self._get_cache_path(video_id)
        safe_dump_to_file(data=info,file_path=cache_path)
        return video_id,cache_path
    def _save_to_info_path(self,data,url=None,video_id=None):
        if not video_id and not url:
            video_id = data.get("id")
        if not video_id and url:
            video_id = data.get("id") or hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        if video_id:
            cache_path = self._get_cache_path(video_id)
            safe_dump_to_file(data=data,file_path=cache_path)
            return video_id,cache_path
    def _get_cached_info(self,url=None,video_id=None):
        cache_path = self._get_cache_path(url=url,video_id=video_id)
        if os.path.isfile(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
    def _add_url_top_registry(self,url,video_id):
        if url:
            self.registry["by_url"][url] = video_id
        self.registry["by_id"][video_id] = {"url": url, "timestamp": time.time()}
        self._save_registry()
    def get_video_info(self, url=None, video_id=None, force_refresh=False,download=False):
        url = get_corrected_url(url=url)
        if not (url or video_id):
            raise ValueError("Either url or video_id must be provided")

        # 1. Lookup video_id from registry if only URL given
        video_id = video_id or self._get_video_id(url=url)

        # 2. If video_id known, check cache
        if video_id:
            cache_path = self._get_cache_path(video_id)
            if os.path.isfile(cache_path) and not force_refresh:
                return self._get_cached_info(url=url,video_id=video_id)
                
        # 3. Otherwise, fetch with yt_dlp
        video_id,cache_path = self._fetch_get_id(url=url)
        # Update registry
        self._add_url_top_registry(url=url,video_id=video_id)

        return self._get_cached_info(url=url,video_id=video_id)
    def edit_info(self,data,url=None,video_id=None, force_refresh=False,download=False):
        video_info = self.get_video_info(url=url, video_id=video_id, force_refresh=force_refresh,download=download)
        video_info.update(data)
        self._save_to_info_path(data=video_info,url=url,video_id=video_id)
        return video_info
    def list_cached_videos(self):
        """Return all cached entries (url, id, metadata)."""
        results = []
        for vid, meta in self.registry["by_id"].items():
            results.append({"video_id": vid, "url": meta["url"], "timestamp": meta["timestamp"]})
        return results



