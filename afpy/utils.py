from functools import partial

import bleach
import markdown2


ALLOWED_TAGS = [
    # Bleach Defaults
    "a",
    "abbr",
    "acronym",
    "b",
    "blockquote",
    "code",
    "em",
    "i",
    "li",
    "ol",
    "strong",
    "ul",
    # Custom Additions
    "br",
    "caption",
    "cite",
    "col",
    "colgroup",
    "dd",
    "del",
    "details",
    "div",
    "dl",
    "dt",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "img",
    "p",
    "pre",
    "span",
    "sub",
    "summary",
    "sup",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "tt",
    "kbd",
    "var",
]

ALLOWED_ATTRIBUTES = {
    # Bleach Defaults
    "a": ["href", "title"],
    "abbr": ["title"],
    "acronym": ["title"],
    # Custom Additions
    "*": ["id"],
    "hr": ["class"],
    "img": ["src", "width", "height", "alt", "align", "class"],
    "span": ["class"],
    "div": ["class"],
    "th": ["align"],
    "td": ["align"],
    "code": ["class"],
    "p": ["align", "class"],
}

ALLOWED_STYLES = []


def markdown_to_html(content):
    return bleach.sanitizer.Cleaner(
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        styles=ALLOWED_STYLES,
        filters=[partial(bleach.linkifier.LinkifyFilter, skip_tags=["pre"], parse_email=False)],
    ).clean(markdown2.markdown(content))
