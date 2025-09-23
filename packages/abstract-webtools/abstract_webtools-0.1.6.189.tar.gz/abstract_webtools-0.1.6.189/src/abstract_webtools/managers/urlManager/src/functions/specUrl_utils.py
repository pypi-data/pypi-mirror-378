from .url_utils import *
def reconstructUrlFromUrlParse(url=None,parsed=None,parsed_dict=None):
    keys = ['scheme','netloc','path','params','query','fragment']
    if url and not parsed:
        parsed_dict = parse_url(url=url)
    if parsed and not parsed_dict:
        parsed_dict = parse_url(parsed=parsed)
    if parsed_dict:
        scheme = parsed_dict.get('scheme')
        nuUrl =''
        for key in keys:
            value = parsed_dict.get(key,'')
            if key  == 'scheme':
                nuUrl += f'{value}://' if value else ''
            elif key  == 'query':
                nuUrl += f'?{reconstructQuery(value)}' if value else ''
            elif key  == 'netloc':
                nuUrl += reconstructNetLoc(value) if value else ''
            else:
                print(value)
                nuUrl += value
        return nuUrl
    return url
def get_youtube_url(url=None,parsed=None, parsed_dict =None ):
    if url and not parsed:
        parsed_dict = parse_url(url=url)
    if parsed and not parsed_dict:
        parsed_dict = parse_url(parsed=parsed)
    if parsed_dict:
        netloc = parsed_dict.get("netloc")
        domain = netloc.get('domain')
        query = parsed_dict.get('query')
        path = parsed_dict.get('path')
        if domain.startswith('youtu'):
            netloc['www']=True
            netloc['domain'] ='youtube'
            netloc['extention'] = '.com'
            parsed_dict['netloc']=netloc
            v_query = query.get('v')
            if path.startswith('/watch'):
                parsed_dict["path"] = f"/{v_query}"
            elif path.startswith('/shorts'):
                parsed_dict["path"] = path[len('/shorts'):]
            parsed_dict["query"] = {"v":eatAll(parsed_dict["path"],['/'])}
            parsed_dict["path"]='/watch'
            return reconstructUrlFromUrlParse(parsed_dict=parsed_dict)
def get_threads_url(url=None,parsed=None, parsed_dict =None ):
    if url and not parsed:
        parsed = parse_url(url)
    if parsed and not parsed_dict:
        parsed_dict = parse_url(parsed=parsed)
    if parsed_dict:
        netloc = parsed_dict.get("netloc")
        domain = netloc.get('domain')
        if domain.startswith('threads'):
            netloc['www']=True
            netloc['domain'] ='youtube'
            netloc['extention'] = '.net'
            parsed['netloc']=netloc
            return reconstructUrlFromUrlParse(url=url,parsed=parsed,parsed_dict=None)  
def get_corrected_url(url=None,parsed=None, parsed_dict =None ):
    if url and not parsed:
        parsed_dict = parse_url(url=url)
    if parsed and not parsed_dict:
        parsed_dict = parse_url(parsed=parsed)
    if parsed_dict:
        funcs = [get_threads_url,get_youtube_url,reconstructUrlFromUrlParse]
        for func in funcs:
            corrected_url = func(url=url,parsed=parsed,parsed_dict=parsed_dict)
            if corrected_url:
                return corrected_url

