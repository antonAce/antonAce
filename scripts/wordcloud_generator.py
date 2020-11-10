# AUTOMATED SCRIPT FOR GENERATING WORDCLOUD
# FOR README.MD FROM TOPICS OF PUBLIC REPOSITORIES

import os
import numpy as np
import matplotlib.pyplot as plt

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image
from json import loads
from requests import get


AUTH_TOKEN = os.getenv('AUTH_TOKEN')
PROFILE_NAME = 'antonace'
GITHUB_ACCEPTABLE_HEADERS = \
    {
        'Accept': 'application/vnd.github.mercy-preview+json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }

WORDCLOUD_IMAGE_FILE_PATH = 'static/png'
WORDCLOUD_MASK_FILE_PATH = WORDCLOUD_IMAGE_FILE_PATH + '/' + 'wordcloud_mask.png'
WORDCLOUD_IMAGE_FILE_NAME = 'wordcloud.png'


def fetch_topics(repository_name: str) -> list:
    topics_response = get(f'https://api.github.com/repos/{PROFILE_NAME}/{repository_name}/topics',
                          headers=GITHUB_ACCEPTABLE_HEADERS)
    topics = loads(str(topics_response.text))
    return [topic.replace('-', '.') for topic in topics['names']]


print('FETCHING REPOSITORIES\' TOPICS')

response = get(f'https://api.github.com/users/{PROFILE_NAME}/repos', headers=GITHUB_ACCEPTABLE_HEADERS)
repositories = loads(str(response.text))
repositories_topics = [' '.join(fetch_topics(repo['name'])) for repo in repositories]
joined_topics = ' '.join(repositories_topics)

print('GENERATING WORDCLOUD FROM TOPICS')

wordcloud_location = WORDCLOUD_IMAGE_FILE_PATH + '/' + WORDCLOUD_IMAGE_FILE_NAME
wordcloud_image = np.array(Image.open(WORDCLOUD_MASK_FILE_PATH))
wordcloud_image = np.where(wordcloud_image == 0, 255, wordcloud_image)

stopwords = set(STOPWORDS)

if not os.path.exists(WORDCLOUD_IMAGE_FILE_PATH):
    os.makedirs(WORDCLOUD_IMAGE_FILE_PATH)

cloud = WordCloud(mask=wordcloud_image, background_color='white',
                  stopwords=stopwords, max_words=1000).generate(joined_topics)

cloud_color_scheme = ImageColorGenerator(wordcloud_image)
cloud.recolor(color_func=cloud_color_scheme)

cloud.to_file(wordcloud_location)

print('WORDCLOUD SAVED SUCCESSFULLY')
