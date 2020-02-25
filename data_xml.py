import email
import time
from xml.etree import ElementTree

from werkzeug.utils import secure_filename

import common

for category in common.CATEGORIES:
    for state in common.STATES:
        (common.POSTS_DIR / category / state).mkdir(parents=True, exist_ok=True)


def get_path(category, state, timestamp, *args, create_dir=False):
    path = common.POSTS_DIR / category / state / timestamp
    if create_dir:
        path.mkdir(parents=True, exist_ok=True)
    for arg in args:
        path /= arg
    return path


def count_posts(category, state=common.STATE_PUBLISHED):
    return len(tuple((common.POSTS_DIR / category / state).iterdir()))


def get_posts(category, state=common.STATE_PUBLISHED, page=None, end=None):
    start = 0
    if page and not end:
        end = page * common.PAGINATION
        start = end - common.PAGINATION
    path = common.POSTS_DIR / category / state
    timestamps = sorted(path.iterdir(), reverse=True)
    timestamps = timestamps[start:end] if end else timestamps[start:]
    for timestamp in timestamps:
        post = get_post(category, timestamp.name, state)
        if post:
            yield post


def get_post(category, timestamp, states=None):
    states = tuple(
        states if isinstance(states, (tuple, list)) else
        [states] if isinstance(states, str) else
        common.STATES.keys()
    )
    for state in states:
        dir = common.POSTS_DIR / category / state / timestamp
        path = dir / common.BASE_FILE
        if path.is_file():
            break
    else:
        return None
    tree = ElementTree.parse(path)
    post = {item.tag: (item.text or '').strip() for item in tree.iter()}

    # Calculated fields
    image = post.get('image') or post.get('old_image') or common.BASE_IMAGE
    if (dir / image).is_file():
        post[common.FIELD_IMAGE] = '/'.join((category, state, timestamp, image))
    post[common.FIELD_TIMESTAMP] = timestamp
    post[common.FIELD_STATE] = state
    post[common.FIELD_DIR] = dir
    post[common.FIELD_PATH] = path
    return post


def save_post(category, timestamp, admin, form, files):
    if timestamp is None:
        status = common.STATE_WAITING
        timestamp = str(int(time.time()))
    elif get_path(
            category, common.STATE_WAITING,
            timestamp, common.BASE_FILE).is_file():
        status = common.STATE_WAITING
    elif get_path(
            category, common.STATE_PUBLISHED,
            timestamp, common.BASE_FILE).is_file():
        status = common.STATE_PUBLISHED
    elif get_path(
            category, common.STATE_TRASHED,
            timestamp, common.BASE_FILE).is_file():
        status = common.STATE_TRASHED
    else:
        raise common.DataException(http_code=404)

    if status == common.STATE_PUBLISHED and not admin:
        raise common.DataException(http_code=401)

    post = get_path(category, status, timestamp, common.BASE_FILE, create_dir=True)
    tree = ElementTree.Element('entry')

    for key, value in form.items():
        if key.startswith('_'):
            continue
        element = ElementTree.SubElement(tree, key)
        element.text = value

    if '_image_path' in form:
        image_path = common.POSTS_DIR / form['_image_path']
        if common.ACTION_DELETE_IMAGE in form and image_path.exists():
            image_path.unlink()
            element = ElementTree.SubElement(tree, 'image')
            element.text = ''
        else:
            element = ElementTree.SubElement(tree, 'image')
            element.text = image_path.name
    if 'image' in files and files['image'].filename:
        post_image = files['image']
        filename = secure_filename(post_image.filename)
        post_image.save(str(post.parent / filename))
        element = ElementTree.SubElement(tree, 'image')
        element.text = filename

    element = ElementTree.SubElement(tree, common.STATE_PUBLISHED)
    element.text = email.utils.formatdate(int(timestamp) if timestamp else time.time())
    ElementTree.ElementTree(tree).write(post)

    if common.ACTION_TRASH in form and status == common.STATE_PUBLISHED:
        (common.POSTS_DIR / category / common.STATE_PUBLISHED / timestamp).rename(
            common.POSTS_DIR / category / common.STATE_TRASHED / timestamp
        )
    if not admin and common.ACTION_EDIT in form and status == common.STATE_PUBLISHED:
        (common.POSTS_DIR / category / common.STATE_PUBLISHED / timestamp).rename(
            common.POSTS_DIR / category / common.STATE_WAITING / timestamp
        )

    if admin:

        if common.ACTION_PUBLISH in form and status == common.STATE_WAITING:
            (common.POSTS_DIR / category / common.STATE_WAITING / timestamp).rename(
                common.POSTS_DIR / category / common.STATE_PUBLISHED / timestamp
            )
        elif common.ACTION_UNPUBLISH in form and status == common.STATE_PUBLISHED:
            (common.POSTS_DIR / category / common.STATE_PUBLISHED / timestamp).rename(
                common.POSTS_DIR / category / common.STATE_WAITING / timestamp
            )
        elif common.ACTION_REPUBLISH in form and status == common.STATE_TRASHED:
            (common.POSTS_DIR / category / common.STATE_TRASHED / timestamp).rename(
                common.POSTS_DIR / category / common.STATE_PUBLISHED / timestamp
            )

    return get_post(category, timestamp)
