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
    """Singleton for managing video registry index."""

    def __init__(self, video_directory=None, envPath=None, info_directory=None):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.videoDirectory = get_video_directory(video_directory=video_directory, envPath=envPath)
            self.infoRegistryDirectory = get_info_directory(directory=info_directory, envPath=envPath)
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

    def _get_cache_dir(self, video_id):
        return os.path.join(self.videoDirectory, video_id)

    def get_video_info(self, url=None, video_id=None, force_refresh=False):
        if url:
            video_id = self.registry["by_url"].get(url, video_id)

        if video_id:
            dirbase = self._get_cache_dir(video_id)
            info_path = os.path.join(dirbase, "info.json")
            if os.path.isfile(info_path) and not force_refresh:
                return safe_read_from_json(info_path)

        return None

    def edit_info(self, data, url=None, video_id=None):
        video_id = video_id or data.get("video_id")
        if not video_id:
            raise ValueError("video_id required to update registry")

        dirbase = self._get_cache_dir(video_id)
        os.makedirs(dirbase, exist_ok=True)

        # Save info.json
        info_path = os.path.join(dirbase, "info.json")
        current_info = safe_read_from_json(info_path) or {}
        current_info.update(data)
        safe_dump_to_file(current_info, info_path)

        # Update registry index
        if url:
            self.registry["by_url"][url] = video_id
        self.registry["by_id"][video_id] = {
            "url": url,
            "dir": dirbase,
            "timestamp": time.time()
        }
        self._save_registry()
        return current_info



