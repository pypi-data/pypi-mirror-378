from .functions import *
from .download_utils import *
from .image_utils import *
def optimize_video_for_safari(input_file, reencode=False):
    """
    Optimizes an MP4 file for Safari by moving the 'moov' atom to the beginning.
    Optionally, re-encodes the video for maximum compatibility.
    
    Args:
        input_file (str): Path to the original MP4 file.
        reencode (bool): If True, re-encode the video for Safari compatibility.
        
    Returns:
        str: Path to the optimized MP4 file.
    """
    tmp_dir = tempfile.mkdtemp()
    try:
        local_input = os.path.join(tmp_dir, os.path.basename(input_file))
        shutil.copy2(input_file, local_input)
        
        base, ext = os.path.splitext(local_input)
        local_output = f"{base}_optimized{ext}"
        
        if reencode:
            # Re-encoding command for maximum Safari compatibility
            command = [
                "ffmpeg", "-i", local_input,
                "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k",
                "-movflags", "faststart",
                local_output
            ]
        else:
            # Simple faststart with stream copy
            command = [
                "ffmpeg", "-i", local_input,
                "-c", "copy", "-movflags", "faststart",
                local_output
            ]
        
        try:
            subprocess.run(command, check=True)
            shutil.copy2(local_output, input_file)
            print(f"Optimized video saved as {input_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error during optimization: {e}")
        return input_file
    finally:
        shutil.rmtree(tmp_dir)




def dl_video(url, download_directory=None, output_filename=None,
             get_info=None, download_video=None, ydl_opts=None):
    mgr = get_video_info(
        url,
        download_directory=download_directory,
        output_filename=output_filename,
        get_info=get_info,
        download_video=download_video,
        ydl_opts=ydl_opts,  # pass through
    )
    return get_video_info_from_mgr(mgr)
def for_dl_video(url,download_directory=None,output_filename=None,get_info=None,download_video=None):
    get_info = bool_or_default(get_info,default=True)
    download_video =bool_or_default(download_video,default=True)
    video_mgr = dl_video(url,download_directory=download_directory,output_filename=output_filename,get_info=get_info,download_video=download_video)
    if get_video_info_from_mgr(video_mgr):
        return video_mgr
    videos = soupManager(url).soup.find_all('video')
    for video in videos:
        src = video.get("src")
        video_mgr = dl_video(src,download_directory=download_directory,output_filename=output_filename,download_video=download_video)
        if get_video_info_from_mgr(video_mgr):
            return video_mgr
def downloadvideo(url, directory=None,output_filename=None, rename_display=None, thumbnails=None, audio=None,safari_optimize=None,download_video=None,*args,**kwargs):
    rename_display = bool_or_default(rename_display)
    thumbnails= bool_or_default(thumbnails)
    audio= bool_or_default(thumbnails,default=False)
    safari_optimize=bool_or_default(thumbnails,default=True)
    download_video =bool_or_default(download_video,default=True)
    output_filename = output_filename or get_temp_file_name(url)
    video_mgr = for_dl_video(url,download_directory=directory,output_filename=output_filename,download_video=download_video)
    info = video_mgr.info
    display_id = get_display_id(info)
    os.makedirs(directory, exist_ok=True)
    video_directory = os.path.join(directory, display_id)
    os.makedirs(video_directory, exist_ok=True)
    info['file_path'] = video_directory
    if info:
        file_path = info.get('file_path')
    if rename_display and file_path:
        # Rename using metadata
        video_id = info.get('id', get_temp_id(url))
        title = output_filename or get_video_title(info)
        safe_title = get_safe_title(title)
        final_filename = output_filename or f"{safe_title}_{video_id}"
        final_filename = f"{final_filename}.mp4"
        new_path = os.path.join(video_directory, final_filename)
        if os.path.exists(info['file_path']):
            os.rename(info['file_path'], new_path)
            info['file_path'] = new_path
        info['file_path'] = new_path
            
            # *** Here we call the optimization function ***
    video_path = info.get('file_path')
    if video_path and video_path.lower().endswith('.mp4') and safari_optimize:
        info['file_path'] = optimize_video_for_safari(video_path,reencode=safari_optimize)
    info_path = os.path.join(video_directory, 'info.json')
    if thumbnails:
        info = get_thumbnails(video_directory, info)
    if audio:
        try:
            info = download_audio(directory, info)
        except:
            info['audio_path'] = None
    info['json_path'] = info_path
    safe_dump_to_file(info, info_path)
    return info

