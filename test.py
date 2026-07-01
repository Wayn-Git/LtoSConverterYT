
import re
import requests
from pprint import pprint

url = "https://www.youtube.com/watch?v=S0ZaiGLCMoM"
# html = requests.get(url).text


# output = re.search(f'<title>(.*?)</title>', html).group(1)
# print(output)


# url_split = url.split("=")
# print(url_split)
# url_joined = ",".join(url_split)

# print(url_joined)

from pytubefix import YouTube

yt = YouTube(url)
print(yt.title)