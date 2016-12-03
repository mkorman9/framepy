
def normalize_url(url):
    if not url.endswith('/'):
        url += '/'
    return url
