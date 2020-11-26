import bleach
import markdown2


def markdown_to_html(content):
    return bleach.sanitizer.Cleaner().clean(markdown2.markdown(content))
