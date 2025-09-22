##import threading,os,re,yt_dlp
from ..imports import *
from .domain_utils import *
def reconstructNetLoc(netloc):
    nunetloc=''
    keys = ['www','domain','extention']
    if isinstance(netloc,dict):
        for i,key in enumerate(keys):
           value = netloc.get(key)
           if key == 'www':
               value = 'www' if value else ''
           keys[i] = eatAll(value,['.'])
        netloc = eatAll('.'.join(keys),['.'])
    return netloc
def reconstructQuery(query):
    if isinstance(query,dict):
        nuquery = ''
        for key,value in query.items():
            nuquery+=f"{key}={value}"
        query=nuquery
    return query
def reconstructUrlParse(url=None,parsed=None,parsed_dict=None):
    parsed_dict = parse_url(url=url,parsed=parsed,parsed_dict=parsed_dict)
    keys = ['netloc','query']
    for i,key in enumerate(keys):
        value = parsed_dict.get(key)
        if key == 'netloc':
            parsed_dict['netloc']=reconstructNetLoc(value)
        elif key == 'query':
            parsed_dict['query']=reconstructQuery(value)
    return parsed_dict


def dictquery(parsed):
    query = parsed.query if hasattr(parsed, "query") else parsed

    nuqueries = {}
    for pair in query.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            nuqueries[k] = v
        else:
            nuqueries[pair] = ""
    return nuqueries
def parse_netloc(url=None,parsed=None,netloc=None):
    netloc = get_extention(url=url,parsed=parsed,netloc=netloc)
    www=False
    nunetloc={'www':www}
    nunetloc.update(netloc)
    domain = nunetloc.get("domain")
    if domain.startswith('www.'):
        nunetloc['domain']=domain[len('www.'):]
        www = True
    nunetloc['www'] = www
    return nunetloc
def parse_url(url=None,parsed=None,parsed_dict=None):
    """
    Parse URL into dict, applying ALL_URL_KEYS defaults.
    """
    if parsed_dict:
        return parsed_dict
    if url and not parsed:
        parsed = urlparse(url)

    if parsed:
        scheme, netloc, path = parsed.scheme, parsed.netloc, parsed.path

        # Handle case: bare "example"
        if not scheme and not netloc and path:
            netlocs = [piece for piece in path.split("/") if piece]
            if netlocs:
                netloc = netlocs[0]
                path = f"/{'/'.join(netlocs[1:])}" if len(netlocs) > 1 else ""
            parsed = parsed._replace(netloc=netloc, path=path)

        # cycle through schemes
        scheme = scheme or ALL_URL_KEYS["scheme"][0]

        netloc_data = get_extention(parsed=parsed, options=ALL_URL_KEYS["netloc"])

        return {
            "scheme": scheme,
            "netloc": netloc_data,
            "path": parsed.path,
            "params": parsed.params,
            "query": dictquery(parsed),
            "fragment": parsed.fragment,
        }

