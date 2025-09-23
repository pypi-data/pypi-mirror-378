import re

from bs4 import BeautifulSoup
from django.conf import settings


class HtmlSanitizer:
    whitelist_tags = ('a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'a', 'iframe')
    whitelist_attrs = ('href', 'id', 'src', 'name', 'width', 'height', 'alt')
    whitelist_classes = ('toc',)

    """
    Clean up class for extracting unwanted content from text, which was posted by users
    """
    def __init__(self, text, **kwargs):
        self.kwargs = kwargs
        self.soup = BeautifulSoup(text, "lxml") if text else None

    def _extract_tags(self, tags=()):
        for tag in tags:
            for current_tag in self.soup.find_all(tag):
                current_tag.extract()

    def _remove_all_attrs_except_saving(self, whitelist_tags=(), whitelist_attrs=(), whitelist_classes=()):
        for tag in self.soup.find_all(True):
            saved_classes = []
            if tag.has_attr('class'):
                classes = tag['class']
                for class_str in whitelist_classes:
                    if class_str in classes:
                        saved_classes.append(class_str)

            if tag.name not in whitelist_tags:
                tag.attrs = {}
            else:
                attrs = dict(tag.attrs)
                for attr in attrs:
                    if attr not in whitelist_attrs:
                        del tag.attrs[attr]

            if len(saved_classes) > 0:
                tag['class'] = ' '.join(saved_classes)

    def _add_rel_attr(self, tag, attr):
        site_url = getattr(settings, "SITE_URL", '/')
        for tag in self.soup.find_all(tag):
            attr_content = tag.get(attr)
            if attr_content and not attr_content.startswith(site_url) and not attr_content.startswith('/'):
                tag['rel'] = 'nofollow'

    def _add_class_attr(self, tag, classes=()):
        for tag in self.soup.find_all(tag):
            saved_classes = []
            if tag.has_attr('class'):
                saved_classes.append(tag['class'])
            saved_classes.extend(list(classes))
            tag['class'] = ' '.join(saved_classes)

    def _add_attr(self, tag, attr, value):
        for tag in self.soup.find_all(tag):
            tag[attr] = value

    def _correct_url(self, tag, attr):
        site_url = getattr(settings, "SITE_URL", None)
        languages = getattr(settings, "LANGUAGES", None)

        if site_url is not None and languages is not None and len(languages) > 1:
            site_url_parser = re.compile('({})'.format('|'.join(['^{}/{}'.format(site_url, code) for code, language in languages])))
            relational_url_parser = re.compile('({})'.format('|'.join(['^/{}'.format(code) for code, language in languages])))

            for tag in self.soup.find_all(tag):
                attr_content = tag.get(attr)
                if attr_content:
                    attr_content = site_url_parser.sub(site_url, attr_content)
                    attr_content = relational_url_parser.sub('', attr_content)
                    tag[attr] = attr_content

    def clean(self):
        if not self.soup:
            return ''

        self._extract_tags(tags=('script', 'style'))
        self._remove_all_attrs_except_saving(
            whitelist_tags=self.whitelist_tags,
            whitelist_attrs=self.whitelist_attrs,
            whitelist_classes=self.whitelist_classes
        )
        self._add_rel_attr(tag='a', attr='href')
        self._add_rel_attr(tag='img', attr='src')
        self._correct_url(tag='a', attr='href')
        self._correct_url(tag='img', attr='src')
        self._add_attr(tag='img', attr='loading', value='lazy')

        class_config = getattr(settings, 'MARKDOWN_FIELD_SANITIZER_CONFIG', {})
        for tag, classes in class_config.items():
            self._add_class_attr(tag=tag, classes=classes)

        if self.soup.body:
            return self.soup.body.decode_contents()
        return self.soup.decode_contents()
