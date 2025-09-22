from .url_utils import *
def reconstructUrlFromUrlParse(url=None,parsed=None):
    keys = ['scheme','netloc','path','params','query','fragment']
    if url and not parsed:
        parsed = parse_url(url)
    if parsed:
        parsed = reconstructUrlParse(parsed)
        scheme = parsed.get('scheme')
        nuUrl =''
        for key in keys:
            value = parsed.get(key,'')
            if key  == 'scheme':
                nuUrl += f'{value}://' if value else ''
            elif key  == 'query':
                nuUrl += f'?{value}' if value else ''
            else:
                nuUrl += value
        return nuUrl
    return url
def get_youtube_url(url=None,parsed=None):
    if url and not parsed:
        parsed = parse_url(url)
    if parsed:
        netloc = parsed.get("netloc")
        domain = netloc.get('domain')
        query = parsed.get('query')
        path = parsed.get('path')
        if domain.startswith('youtu'):
            netloc['www']=True
            netloc['domain'] ='youtube'
            netloc['extention'] = '.com'
            parsed['netloc']=netloc
            v_query = query.get('v')
            if path.startswith('/watch'):
                parsed["path"] = f"/{v_query}"
            elif path.startswith('/shorts'):
                parsed["path"] = path[len('/shorts'):]
            parsed["query"] = {"v":eatAll(parsed["path"],['/'])}
            parsed["path"]='/watch'
            return reconstructUrlFromUrlParse(parsed)
def get_threads_url(url=None,parsed=None):
    if url and not parsed:
        parsed = parse_url(url)
    if parsed:
        netloc = parsed.get("netloc")
        domain = netloc.get('domain')
        if domain.startswith('threads'):
            netloc['www']=True
            netloc['domain'] ='youtube'
            netloc['extention'] = '.net'
            parsed['netloc']=netloc
            return reconstructUrlFromUrlParse(parsed)   
def get_corrected_url(url=None,parsed=None):
    if url and not parsed:
        parsed = parse_url(url)
    if parsed:
        funcs = [get_threads_url,get_youtube_url,reconstructUrlFromUrlParse]
        for func in funcs:
            corrected_url = func(url=url,parsed=parsed)
            if corrected_url:
                return corrected_url

