import re
from urllib.parse import urlparse, parse_qs


def get_youtube_id(url):
    # YouTube video ID'sini çıkarmak için düzenli ifade
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')

    youtube_regex_match = re.match(youtube_regex, url)

    if youtube_regex_match:
        return youtube_regex_match.group(6)
    else:
        # URL parametrelerini kullanarak kontrol et
        query = urlparse(url)
        if 'v' in parse_qs(query.query):
            return parse_qs(query.query)['v'][0]
        elif 'youtu.be' in query.netloc:
            return query.path[1:]
        else:
            return None
