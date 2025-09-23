from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save

from django.utils.module_loading import import_string

class MarkdownField(models.TextField):
    """
    This field save markdown text with auto-populate text to html field.
    This field must be used with second text field for html content.
    This field support django-modeltranslation package.
    """

    def set_markdown(self, instance=None, update_fields=None, **kwargs):
        markdown_text = getattr(instance, self.attname)
        if markdown_text and len(markdown_text) > 0:
            languages = getattr(settings, "LANGUAGES", None)
            codes = tuple([code.replace("-", "_") for code, language in languages])

            worker = self.markdown_worker(
                text=markdown_text,
                instance=instance,
                html_sanitizer=self.html_sanitizer,
                **kwargs
            )
            html_text = worker.generate_html()

            if 'modeltranslation' in settings.INSTALLED_APPS and self.name.endswith(codes):
                offset = 2
                for code in codes:
                    if self.name.endswith(code):
                        offset = len(code)

                instance.__dict__['{}_{}'.format(self.html_field, self.name[-offset:])] = html_text
            else:
                instance.__dict__[self.html_field] = html_text

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        pre_save.connect(self.set_markdown, sender=cls)

    def __init__(self, html_field=None, markdown_worker=None, html_sanitizer=None, *args, **kwargs):
        self.html_field = html_field
        self.markdown_worker = markdown_worker if markdown_worker else import_string(getattr(settings, 'MARKDOWN_FIELD_WORKER', 'django_markdown_html_field.worker.MarkdownWorker'))
        self.html_sanitizer = html_sanitizer if html_sanitizer else import_string(getattr(settings, 'MARKDOWN_FIELD_SANITIZER' ,'django_markdown_html_field.sanitizer.HtmlSanitizer'))
        super().__init__(*args, **kwargs)
