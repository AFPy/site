import email
import time
from xml.etree import ElementTree

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


def get_posts(category, state=common.STATE_PUBLISHED, start=0, end=None):
    path = common.POSTS_DIR / category / state
    timestamps = sorted(path.iterdir(), reverse=True)
    timestamps = timestamps[start:end] if end else timestamps[start:]
    for timestamp in timestamps:
        yield get_post(category, timestamp.name, state)


def get_post(category, timestamp, states=None):
    states = tuple(
        states
        if isinstance(states, (tuple, list))
        else [states]
        if isinstance(states, str)
        else common.STATES.keys()
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


def save_post(category, timestamp, admin, **data):
    if timestamp is None:
        status = common.STATE_WAITING
        timestamp = str(int(time.time()))
    elif get_path(category, common.STATE_WAITING, timestamp, common.BASE_FILE).is_file():
        status = common.STATE_WAITING
    elif get_path(category, common.STATE_PUBLISHED, timestamp, common.BASE_FILE).is_file():
        status = common.STATE_PUBLISHED
    else:
        raise common.DataException(http_code=404)
    if status == common.STATE_PUBLISHED and not admin:
        raise common.DataException(http_code=401)

    post = get_path(category, status, timestamp, common.BASE_FILE, create_dir=True)
    tree = ElementTree.Element('entry')
    for key, value in data.items():
        if key.startswith('_'):
            continue
        element = ElementTree.SubElement(tree, key)
        element.text = value
    element = ElementTree.SubElement(tree, common.STATE_PUBLISHED)
    element.text = email.utils.formatdate(
        int(timestamp) if timestamp else time.time()
    )
    ElementTree.ElementTree(tree).write(post)

    if admin:
        if common.ACTION_PUBLISH in data and status == common.STATE_WAITING:
            (common.POSTS_DIR / category / common.STATE_WAITING / timestamp).rename(
                common.POSTS_DIR / category / common.STATE_PUBLISHED / timestamp
            )
        elif common.ACTION_UNPUBLISH in data and status == common.STATE_PUBLISHED:
            (common.POSTS_DIR / category / common.STATE_PUBLISHED / timestamp).rename(
                common.POSTS_DIR / category / common.STATE_WAITING / timestamp
            )

    return get_post(category, timestamp)


def add_image(category, state, timestamp, image):
    path = get_path(category, state, timestamp)
    if not path.is_dir():
        return common.DataException(http_code=401)
    post = get_post(category, timestamp, states=state)
    if not post:
        return common.DataException(http_code=404)
    image.save(post[common.FIELD_DIR], image.filename)
    image_path = f'{timestamp}.{image.filename}'
    image.save(common.IMAGE_DIR, image_path)
    save_post(category, state, timestamp, old_image=image.filename, image=image_path)
