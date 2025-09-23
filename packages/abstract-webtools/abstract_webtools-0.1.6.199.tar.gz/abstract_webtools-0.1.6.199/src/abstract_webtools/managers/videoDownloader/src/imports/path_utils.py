from .imports import *
DIRBASES = {
    "temp":{
        "envKey":"VIDEO_TEMP_DIRECTORY",
        "dirbase":"temp"
        },
    "download":{
        "envKey":"VIDEO_DOWNLOADS_DIRECTORY",
        "dirbase":"downloads"
        },
    "info":{
        "envKey":"VIDEO_INFO_DIRECTORY",
        "dirbase":"info_registry"
        },
    "data":{
        "envKey":"VIDEO_DATA_DIRECTORY",
        "dirbase":"data"
        },
    "video":{
        "envKey":"VIDEO_DIRECTORY",
        "dirname":os.path.expanduser("~"),
        "dirbase":"videos",
        "directory":os.path.join(os.path.expanduser("~"), "videos")
        }
    }
def get_dirbase_data(key=None,directory=None,envKey=None):
    dirbase_data = DIRBASES.get(key,{})
    key = key or dirbase_data.get("dirbase")
    envKey = envKey or dirbase_data.get("envKey")
    directory = directory or dirbase_data.get("directory")
    return directory,key,envKey
def derive_spec_directory(spec_dir,video_directory=None):
    """Default downloads under <video_directory>/videos."""
    video_directory = video_directory or derive_video_directory()
    return os.path.join(video_directory, spec_dir)
def get_spec_directory(directory=None, key=None,envKey=None, envPath=None):
    """Get or create the video download directory."""
    directory = (
        directory
        or get_env_value(key=envKey, path=envPath)
        or derive_spec_directory(key)
    )
    os.makedirs(directory, exist_ok=True)
    return directory



# 🔹 NEW: for downloads
def derive_download_directory(key=None,video_directory=None):
    """Default downloads under <video_directory>/videos."""
    directory,spec_dir,envKey = get_dirbase_data(key='download',directory=video_directory)
    return derive_spec_directory(
        spec_dir=spec_dir,
        video_directory=directory,
        )
def derive_data_directory(key=None,video_directory=None):
    """Default downloads under <video_directory>/videos."""
    directory,spec_dir,envKey = get_dirbase_data(key='data',directory=video_directory)
    return derive_spec_directory(
        spec_dir=spec_dir,
        video_directory=directory,
        )

def derive_temp_directory(key=None,video_directory=None):
    """Default downloads under <video_directory>/videos."""
    directory,spec_dir,envKey = get_dirbase_data(key='temp',directory=video_directory)
    return derive_spec_directory(
        spec_dir=spec_dir,
        video_directory=directory,
        )

def derive_info_registry(key=None,video_directory=None):
    """Default downloads under <video_directory>/videos."""
    directory,spec_dir,envKey = get_dirbase_data(key='info',directory=video_directory)
    return derive_spec_directory(
        spec_dir=spec_dir,
        video_directory=directory,
        )
def derive_video_directory(key=None,video_directory=None):
    """Default downloads under <video_directory>/videos."""
    directory,spec_dir,envKey = get_dirbase_data(key='video',directory=video_directory)
    return derive_spec_directory(
        spec_dir=spec_dir,
        video_directory=directory,
        )


def get_video_directory(key=None,video_directory=None,  envPath=None):
    """Get or create the main video directory."""
    key = key or DIRBASES.get("video",{}).get("envKey")
    video_directory = (
        video_directory
        or get_env_value(key=key, path=envPath)
        or derive_video_directory()
    )
    os.makedirs(video_directory, exist_ok=True)
    return video_directory
def get_download_directory(
    directory=None,
    envKey=None,
    key=None,
    envPath=None,
    **kwargs
    ):
    """Get or create the video download directory."""
    directory,key,envKey = get_dirbase_data(
        key='download',  # ✅ FIXED (singular to match DIRBASES)
        directory=directory or kwargs.get('download_directory'),
        envKey=envKey
    )
    return get_spec_directory(
        directory=directory,
        key=key,
        envKey=envKey,
        envPath=envPath
    )

def get_info_directory(
    directory=None,
    envKey=None,
    key=None,
    envPath=None,
    **kwargs
    ):
    """Get or create the info registry directory."""
    directory,key,envKey = get_dirbase_data(key='info',directory=directory or kwargs.get('info_directory'),envKey=envKey)
    return get_spec_directory(
        directory=directory,
        key=key,
        envKey=envKey,
        envPath=envPath
        )
def get_temp_directory(
    directory=None,
    key=None,
    envKey=None,
    envPath=None,
    **kwargs
    ):
    """Get or create the video download directory."""
    directory,key,envKey = get_dirbase_data(key='temp',directory=directory or kwargs.get('temp_directory'),envKey=envKey)
    return get_spec_directory(
        directory=directory,
        key=key,
        envKey=envKey,
        envPath=envPath
        )
def get_data_directory(
    directory=None,
    key=None,
    envKey=None,
    envPath=None,
    **kwargs
    ):
    """Get or create the video download directory."""
    directory,key,envKey = get_dirbase_data(key='data',directory=directory or kwargs.get('data_directory'),envKey=envKey)
    return get_spec_directory(
        directory=directory,
        key=key,
        envKey=envKey,
        envPath=envPath
        )
