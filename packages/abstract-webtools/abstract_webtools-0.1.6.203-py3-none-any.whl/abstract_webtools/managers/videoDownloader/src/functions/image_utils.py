from ..imports import *
def download_image(url, save_path=None):
    """
    Downloads an image from a URL and saves it to the specified path.
    
    Args:
        url (str): The URL of the image to download
        save_path (str, optional): Path to save the image. If None, uses the filename from URL
        
    Returns:
        str: Path where the image was saved, or None if download failed
    """
    try:
        # Send GET request to the URL
        response = requests.get(url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Set decode_content=True to automatically handle Content-Encoding
            response.raw.decode_content = True
            
            # If no save_path provided, extract filename from URL
            if save_path is None:
                # Get filename from URL
                filename = url.split('/')[-1]
                save_path = filename
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Write the image content to file
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"Image successfully downloaded to {save_path}")
            return save_path
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {str(e)}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None
def get_thumbnails(directory,info):
    thumbnails_dir = os.path.join(directory,'thumbnails')
    os.makedirs(thumbnails_dir, exist_ok=True)
    thumbnails = info.get('thumbnails',[])
    for i,thumbnail_info in enumerate(thumbnails):
        thumbnail_url = thumbnail_info.get('url')
        thumbnail_base_url = thumbnail_url.split('?')[0]
        baseName = os.path.basename(thumbnail_base_url)
        fileName,ext = os.path.splitext(baseName)
        baseName = f"{fileName}{ext}"
        resolution = info['thumbnails'][i].get('resolution')
        if resolution:
            baseName = f"{resolution}_{baseName}"
        img_id = info['thumbnails'][i].get('id')
        if img_id:
            baseName = f"{img_id}_{baseName}"
        thumbnail_path = os.path.join(thumbnails_dir,baseName)
        info['thumbnails'][i]['path']=thumbnail_path
        download_image(thumbnail_url, save_path=thumbnail_path)
    return info
