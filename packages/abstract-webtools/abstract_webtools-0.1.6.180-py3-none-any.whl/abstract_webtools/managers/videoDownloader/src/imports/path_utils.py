from .imports import *
def derive_video_directory():
    """Default to ~/videos if nothing else is set."""
    return os.path.join(os.path.expanduser("~"), "videos")

def get_video_directory(video_directory=None, key=None, envPath=None):
    """Get or create the main video directory."""
    key = key or "VIDEO_DIRECTORY"
    video_directory = (
        video_directory
        or get_env_value(key=key, path=envPath)
        or derive_video_directory()
    )
    os.makedirs(video_directory, exist_ok=True)
    return video_directory

def derive_info_registry(video_directory=None):
    """Default info_registry under the video directory."""
    video_directory = video_directory or derive_video_directory()
    return os.path.join(video_directory, "info_registry")

def get_info_directory(info_directory=None, key=None, envPath=None):
    """Get or create the info registry directory."""
    key = key or "INFO_DIRECTORY"
    info_directory = (
        info_directory
        or get_env_value(key=key, path=envPath)
        or derive_info_registry()
    )
    os.makedirs(info_directory, exist_ok=True)
    return info_directory
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
