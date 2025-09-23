import markdown
from slugify import slugify


def cyrillic_slugify(value, separator):
    return slugify(value, separator=separator)


class MarkdownWorker:
    """
    Markdown converter. It will convert markdown text to html text with clean up from unwanted content, using ESoap class
    """

    extensions = [
        'attr_list',
        'tables',
        'fenced_code',
        'nl2br',
        'toc',
        'django_markdown_html_field.extensions.super_sub_script',
        'django_markdown_html_field.extensions.video'
    ]

    extension_configs = {
        'toc': {
            'slugify': cyrillic_slugify
        }
    }

    def __init__(self, text, html_sanitizer, instance=None, **kwargs):
        self.markdown_text = text
        self.html_text = None
        self.instance = instance
        self.html_sanitizer = html_sanitizer
        self.kwargs = kwargs

    def __make_html_from_markdown(self):
        if self.markdown_text:
            self.html_text = markdown.markdown(
                self.markdown_text,
                extensions=self.extensions,
                extension_configs=self.extension_configs,
                output_format='html'
            )

    def generate_html(self):
        self.__make_html_from_markdown()
        return self.html_sanitizer(text=self.html_text, **self.kwargs).clean()