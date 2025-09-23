# Django Markdown to HTML Field

A Django model field for handling Markdown content with advanced sanitization and extensions support.

This field converts Markdown to HTML on the model instance save and stores converted HMTL to a specific text field.

## Features

- Markdown field for Django models
- Automatic conversion to HTML, which will be stored in TextField
- Built-in HTML sanitization
- Support for superscript (^text^) and subscript (~text~) syntax
- Configurable HTML tag and attribute whitelisting
- Automatic handling of external links with nofollow
- Lazy loading for images
- Multi-language URL handling
- Support for django-modeltranslation

## Installation

```bash
pip install django-markdown-html-field
```

## Usage

### Register in settings.py

```python
INSTALLED_APPS = [
    ...
    'django_markdown_html_field'
]
```

### Add MarkdownField to your model

```python
from django_markdown_html_field.fields import MarkdownField

class Page(models.Model):
    content = models.TextField(verbose_name='Content', blank=True, null=True)
    content_markdown = MarkdownField(verbose_name='Content - Markdown', html_field='content')
```

In this example, the Markdown content will be stored in the `content_markdown` field and the HTML will be stored in the `content` field.

Conversion will be executed automatically on the model instance save.

### Configuration of classes for html tags

You can configure the classes for html tags in the settings.py file.

```python
MARKDOWN_FIELD_SANITIZER_CONFIG = {
    'img': ('img-fluid', 'd-block', 'mx-auto', 'mw-100', 'mvh-75'),
    'table': ('table', 'table-bordered', 'table-hover')
}
```

### Customize the sanitizer and worker

You can inherit from the sanitizer and worker and implement your own logic.

After that you can register your custom classes in the settings.py file.

For example:

```python
MARKDOWN_FIELD_WORKER = 'your_app.markdown.DoFollowMarkdownWorker'
MARKDOWN_FIELD_SANITIZER = 'your_app.markdown.DoFollowHtmlSanitizer'
```

#### Example of custom worker and sanitizer

```python
from django_markdown_html_field.worker import MarkdownWorker
from django_markdown_html_field.sanitizer import HtmlSanitizer


class DoFollowHtmlSanitizer(HtmlSanitizer):

    def _add_rel_attr(self, tag, attr):
        if self.kwargs.get('dofollow', False):
            return
        super()._add_rel_attr(tag, attr)


class DoFollowMarkdownWorker(MarkdownWorker):

    def __init__(self, text, instance=None, html_sanitizer=None, **kwargs):
        super().__init__(text=text, instance=instance, html_sanitizer=html_sanitizer, **kwargs)
        if instance:
            self.kwargs.update({'dofollow': getattr(instance, 'dofollow', False)})
```

#### Using Custom worker and sanitizer in specific model only

```python
from django_markdown_html_field.fields import MarkdownField
from your_app.markdown import DoFollowMarkdownWorker, DoFollowHtmlSanitizer

class Page(models.Model):
    content = models.TextField(verbose_name='Content', blank=True, null=True)
    content_markdown = MarkdownField(
        verbose_name='Content - Markdown', 
        html_field='content',
        markdown_worker=DoFollowMarkdownWorker,
        html_sanitizer=DoFollowHtmlSanitizer,
    )
```

### Using MarkdownWorker separately

```python
from django.views import View
from django.http import JsonResponse
from django_markdown_html_field.sanitizer import HtmlSanitizer
from django_markdown_html_field.worker import MarkdownWorker

class MarkdownView(View):
    """
    Markdown view for preview html content
    """
    def post(self, request):
        return JsonResponse({'preview': MarkdownWorker(request.POST.get('content'), HtmlSanitizer).generate_html()})
```