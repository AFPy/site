from functools import partial

import bleach
import markdown2


def markdown_to_html(content):
    return bleach.sanitizer.Cleaner(
        filters=[partial(bleach.linkifier.LinkifyFilter, skip_tags=["pre"], parse_email=False)]
    ).clean(markdown2.markdown(content))
