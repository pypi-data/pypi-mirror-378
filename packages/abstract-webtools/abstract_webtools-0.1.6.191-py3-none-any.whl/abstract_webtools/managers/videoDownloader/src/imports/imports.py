import time,json,hashlib,threading,os,re,yt_dlp,urllib.request,m3u8_To_MP4,subprocess,requests,shutil,tempfile
from abstract_utilities import get_logFile,safe_dump_to_file,get_time_stamp,SingletonMeta
from m3u8 import M3U8  # Install: pip install m3u8
from urllib.parse import urljoin
from yt_dlp.postprocessor.ffmpeg import FFmpegFixupPostProcessor
from abstract_math import divide_it,add_it,multiply_it,subtract_it
from ....soupManager import soupManager
from ....urlManager import *
from abstract_security import get_env_value
logger = get_logFile('video_bp')
