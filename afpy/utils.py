from functools import partial

import bleach
import markdown2

ALLOWED_TAGS = ["a", "abbr", "acronym", "b", "blockquote", "code", "em", "i", "li", "ol", "strong", "ul", "p", "br"]


def markdown_to_html(content):
    return bleach.sanitizer.Cleaner(
        tags=ALLOWED_TAGS, filters=[partial(bleach.linkifier.LinkifyFilter, skip_tags=["pre"], parse_email=False)]
    ).clean(markdown2.markdown(content))
