import re
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    if not url:
        return ""
        
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    try:
        parsed = urlparse(url)
        # Force https and normalize netloc (e.g., m.facebook.com to www.facebook.com)
        netloc = parsed.netloc.lower()
        if netloc in ('m.facebook.com', 'mbasic.facebook.com', 'web.facebook.com', 'facebook.com'):
            netloc = 'www.facebook.com'
            
        # Strip tracking query params
        # Keep path only for basic profiles
        path = parsed.path
        if path.endswith('/'):
            path = path[:-1]
            
        return urlunparse(('https', netloc, path, '', '', ''))
    except Exception:
        return url
