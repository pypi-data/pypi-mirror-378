import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor


class SuperSubExtension(Extension):
    def extendMarkdown(self, md):
        # Superscript: ^text^
        md.inlinePatterns.register(Superscript(r'\^([^\^]+)\^'), 'superscript', 175)
        # Subscript: ~text~
        md.inlinePatterns.register(Subscript(r'~([^~]+)~'), 'subscript', 175)


class Superscript(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('sup')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)


class Subscript(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element('sub')
        el.text = m.group(1)
        return el, m.start(0), m.end(0)

def makeExtension(**kwargs):
    return SuperSubExtension(**kwargs)