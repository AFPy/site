import email
import time
from pathlib import Path
from xml.etree import ElementTree
from werkzeug.utils import secure_filename


POST_ACTUALITIES = 'actualites'
POST_JOBS = 'emplois'
POSTS = {POST_ACTUALITIES: "Actualités", POST_JOBS: "Offres d’emploi"}

STATE_WAITING = 'waiting'
STATE_PUBLISHED = 'published'
STATE_TRASHED = 'trashed'
STATES = {
    STATE_WAITING: "En attente",
    STATE_PUBLISHED:  "Publié",
    STATE_TRASHED:  "À la corbeille"
}

ACTION_PUBLISH = 'publish'
ACTION_UNPUBLISH = 'unpublish'
ACTION_REPUBLISH = 'republish'
ACTION_TRASH = 'trash'
ACTION_EDIT = 'edit'
ACTION_DELETE_IMAGE = 'delete_image'
ACTIONS = {
    ACTION_PUBLISH: "Publier",
    ACTION_UNPUBLISH: "Dépublier",
    ACTION_REPUBLISH: "Republier",
    ACTION_TRASH: "Supprimer",
    ACTION_EDIT: 'Editer',
    ACTION_DELETE_IMAGE: "Supprimer l'image"
}

IMAGE = '_image'
TIMESTAMP = '_timestamp'
STATE = '_state'
PATH = '_path'
DIR = '_dir'

BASE_DIR = 'posts'
BASE_FILE = 'post.xml'
BASE_IMAGE = 'post.jpg'


class DataException(Exception):
    def __init__(self, *args, http_code=None, **kwargs):
        self.http_code = http_code
        super().__init__(*args, **kwargs)


root = Path(__file__).parent / BASE_DIR
for category in POSTS:
    for state in STATES:
        (root / category / state).mkdir(parents=True, exist_ok=True)


def get_path(category, state, timestamp, *args, create_dir=False):
    path = root / category / state / timestamp
    if create_dir:
        path.mkdir(exist_ok=True)
    for arg in args:
        path /= arg
    return path


def count_posts(category, state=STATE_PUBLISHED):
    return len(tuple((root / category / state).iterdir()))


def get_posts(category, state=STATE_PUBLISHED, start=0, end=None):
    path = root / category / state
    timestamps = sorted(path.iterdir(), reverse=True)
    timestamps = timestamps[start:end] if end else timestamps[start:]
    for timestamp in timestamps:
        post = get_post(category, timestamp.name, state)
        if post:
            yield post


def get_post(category, timestamp, states=None):
    states = (
        states
        if isinstance(states, (tuple, list))
        else [states]
        if isinstance(states, str)
        else STATES
    )
    for state in states:
        dir = root / category / state / timestamp
        path = dir / BASE_FILE
        if path.is_file():
            break
    else:
        return None
    tree = ElementTree.parse(path)
    post = {item.tag: (item.text or '').strip() for item in tree.iter()}

    # Calculated fields
    image = post.get('image') or BASE_IMAGE
    if (dir / image).is_file():
        post[IMAGE] = '/'.join((category, state, timestamp, image))
    post[TIMESTAMP] = timestamp
    post[STATE] = state
    post[DIR] = dir
    post[PATH] = path
    return post


def save_post(category, timestamp, admin, form, files):
    if timestamp is None:
        status = STATE_WAITING
        timestamp = str(int(time.time()))
    elif get_path(category, STATE_WAITING, timestamp, BASE_FILE).is_file():
        status = STATE_WAITING
    elif get_path(category, STATE_PUBLISHED, timestamp, BASE_FILE).is_file():
        status = STATE_PUBLISHED
    elif get_path(category, STATE_TRASHED, timestamp, BASE_FILE).is_file():
        status = STATE_TRASHED
    else:
        raise DataException(http_code=404)
    if status == STATE_TRASHED and not admin:
        raise DataException(http_code=401)

    post = get_path(category, status, timestamp, BASE_FILE, create_dir=True)
    tree = ElementTree.Element('entry')

    for key, value in form.items():
        if key.startswith('_'):
            continue
        element = ElementTree.SubElement(tree, key)
        element.text = value

    if '_image_path' in form:
        image_path = root / form['_image_path']
        if ACTION_DELETE_IMAGE in form and image_path.exists:
            image_path.unlink()
        else:
            element = ElementTree.SubElement(tree, 'image')
            element.text = image_path.name

    if 'image' in files:
        post_image = files['image']
        filename = secure_filename(post_image.filename) or "image.jpg"
        post_image.save(str(post.parent / filename))
        element = ElementTree.SubElement(tree, 'image')
        element.text = filename

    element = ElementTree.SubElement(tree, STATE_PUBLISHED)
    element.text = email.utils.formatdate(
        int(timestamp) if timestamp else time.time()
    )
    ElementTree.ElementTree(tree).write(post)

    if ACTION_TRASH in form and status == STATE_PUBLISHED:
        (root / category / STATE_PUBLISHED / timestamp).rename(
            root / category / STATE_TRASHED / timestamp
        )
    if not admin and ACTION_EDIT in form and status == STATE_PUBLISHED:
        (root / category / STATE_PUBLISHED / timestamp).rename(
            root / category / STATE_WAITING / timestamp
        )

    if admin:
        if ACTION_PUBLISH in form and status == STATE_WAITING:
            (root / category / STATE_WAITING / timestamp).rename(
                root / category / STATE_PUBLISHED / timestamp
            )
        elif ACTION_UNPUBLISH in form and status == STATE_PUBLISHED:
            (root / category / STATE_PUBLISHED / timestamp).rename(
                root / category / STATE_WAITING / timestamp
            )
        elif ACTION_REPUBLISH in form and status == STATE_TRASHED:
            (root / category / STATE_TRASHED / timestamp).rename(
                root / category / STATE_PUBLISHED / timestamp
            )

    return get_post(category, timestamp)
