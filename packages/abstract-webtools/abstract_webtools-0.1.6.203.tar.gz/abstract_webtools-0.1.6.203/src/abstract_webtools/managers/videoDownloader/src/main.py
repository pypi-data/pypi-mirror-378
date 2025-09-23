from .functions import *
from .imports import *
def get_registryManager(
    video_directory=None,
    envPath=None,
    info_directory=None
    ):
    return infoRegistry(video_directory=video_directory, envPath=envPath, info_directory=info_directory)
def get_video_info(
    url=None,
    video_id=None,
    force_refresh=False,
    video_directory=None,
    envPath=None,
    info_directory=None,
    download=False
    ):
    registryMgr = get_registryManager(video_directory=video_directory, envPath=envPath, info_directory=info_directory)
    return registryMgr.get_video_info(url=url, video_id=video_id, force_refresh=force_refresh)
def get_video_info_spec(
    key=None,
    url=None,
    video_id=None,
    force_refresh=False,
    video_directory=None,
    envPath=None,
    info_directory=None,
    download=None
    ):
    if download:
        VideoDownloader(url=url)
        video_info = get_video_info(
        url=url,
        video_id=video_id,
        force_refresh=force_refresh,
        video_directory=video_directory,
        envPath=envPath,
        info_directory=info_directory,
        download=download)
    video_info = get_video_info(
        url=url,
        video_id=video_id,
        force_refresh=force_refresh,
        video_directory=video_directory,
        envPath=envPath,
        info_directory=info_directory,
        download=download
    )
    if not key:
        return video_info
    value = video_info.get(key)
    if not value:
         value = make_list(get_any_value(video_info,key) or None)[0]
    return value
def get_video_id(
    url=None,
    video_id=None,
    force_refresh=False,
    video_directory=None,
    envPath=None,
    info_directory=None,
    download=False
    ):
    if download:
        VideoDownloader(url=url)
    return get_video_info_spec(
        key='id',
        url=url,
        video_id=video_id,
        force_refresh=force_refresh,
        video_directory=video_directory,
        envPath=envPath,
        info_directory=info_directory,
        download=download
        )
def get_video_title(
    url=None,
    video_id=None,
    force_refresh=False,
    video_directory=None,
    envPath=None,
    info_directory=None,
    download=False
    
    ):
    if download:
        VideoDownloader(url=url)
    return get_video_info_spec(
        key='title',
        url=url,
        video_id=video_id,
        force_refresh=force_refresh,
        video_directory=video_directory,
        envPath=envPath,
        info_directory=info_directory,
        download=download
        )
def get_video_filepath(
    url=None,
    video_id=None,
    force_refresh=False,
    video_directory=None,
    envPath=None,
    info_directory=None,
    download=False
    
    ):
    if download:
        VideoDownloader(url=url)
    return get_video_info_spec(
        key='filepath',
        url=url,
        video_id=video_id,
        force_refresh=force_refresh,
        video_directory=video_directory,
        envPath=envPath,
        info_directory=info_directory,
        download=download
        )


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
