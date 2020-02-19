# coding: utf-8
from pathlib import Path


PAGINATION = 12

PLANET = {
    'Emplois AFPy': 'https://www.afpy.org/feed/emplois/rss.xml',
    'Nouvelles AFPy': 'https://www.afpy.org/feed/actualites/rss.xml',
    'Anybox': 'https://anybox.fr/site-feed/RSS?set_language=fr',
    'Ascendances': 'https://ascendances.wordpress.com/feed/',
    'Code en Seine': 'https://codeenseine.fr/feeds/all.atom.xml',
    'Yaal': 'https://www.yaal.fr/blog/feeds/all.atom.xml',
}

MEETUPS = {
    'amiens': 'https://www.meetup.com/fr-FR/Python-Amiens',
    'bruxelles':
        'https://www.meetup.com/fr-FR/'
        'Belgium-Python-Meetup-aka-AperoPythonBe/',
    'grenoble':
        'https://www.meetup.com/fr-FR/'
        'Groupe-dutilisateurs-Python-Grenoble/',
    'lille': 'https://www.meetup.com/fr-FR/Lille-py/',
    'lyon': 'https://www.meetup.com/fr-FR/Python-AFPY-Lyon/',
    'nantes': 'https://www.meetup.com/fr-FR/Nantes-Python-Meetup/',
    'montpellier': 'https://www.meetup.com/fr-FR/Meetup-Python-Montpellier/',
}

CATEGORY_ACTUALITIES = 'actualites'
CATEGORY_JOBS = 'emplois'
CATEGORIES = {
    CATEGORY_ACTUALITIES: "Actualités",
    CATEGORY_JOBS: "Offres d’emploi",
}

STATE_WAITING = 'waiting'
STATE_PUBLISHED = 'published'
STATE_TRASH = 'trash'
STATES = {
    STATE_WAITING: "En attente",
    STATE_PUBLISHED: "Publié",
    STATE_TRASH: "Supprimé",
}

ACTION_PUBLISH = 'publish'
ACTION_UNPUBLISH = 'unpublish'
ACTIONS = {
    ACTION_PUBLISH: "Publier",
    ACTION_UNPUBLISH: "Dépublier",
}

FIELD_IMAGE = '_image'
FIELD_TIMESTAMP = '_timestamp'
FIELD_STATE = '_state'
FIELD_PATH = '_path'
FIELD_DIR = '_dir'
FIELDS = {
    FIELD_IMAGE: 'image',
    FIELD_TIMESTAMP: 'timestamp',
    FIELD_STATE: 'state',
    FIELD_PATH: 'path',
    FIELD_DIR: 'dir',
}

BASE_DIR = 'posts'
BASE_FILE = 'post.xml'
BASE_IMAGE = 'post.jpg'

ROOT_DIR = Path(__file__).parent
POSTS_DIR = ROOT_DIR / BASE_DIR
IMAGE_DIR = ROOT_DIR / 'images'
IMAGE_DIR.mkdir(exist_ok=True)


class DataException(Exception):
    def __init__(self, *args, http_code=None, **kwargs):
        self.http_code = http_code
        super().__init__(*args, **kwargs)
