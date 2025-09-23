import xml.etree.ElementTree as etree

from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor


class VideoExtension(Extension):

    def add_inline(self, md, name, klass, pattern):
        md.inlinePatterns.register(klass(pattern, md), name, 175)

    def extendMarkdown(self, md):
        self.add_inline(md, 'dailymotion', Dailymotion,
                        r'([^(]|^)https?://www\.dailymotion\.com/video/(?P<dailymotionid>[a-zA-Z0-9]+)(_[\w\-]*)?')
        self.add_inline(md, 'metacafe', Metacafe,
                        r'([^(]|^)https://www\.metacafe\.com/watch/(?P<metacafeid>\d+)/?(:?.+/?)')
        self.add_inline(md, 'vimeo', Vimeo,
                        r'([^(]|^)https://(www\.)?vimeo\.com/(?P<vimeoid>\d+)\S*')
        self.add_inline(md, 'youtube', Youtube,
                        r'([^(]|^)https?://www\.youtube\.com/watch\?\S*v=(?P<youtubeid>\S[^&/]+)')
        self.add_inline(md, 'youtube_short', Youtube,
                        r'([^(]|^)https?://youtu\.be/(?P<youtubeid>\S[^?&/]+)?')


class Dailymotion(InlineProcessor):
    def handleMatch(self, m, data):
        el = render_video('//www.dailymotion.com/embed/video/{}'.format(m.group('dailymotionid')))
        return el, m.start(0), m.end(0)


class Metacafe(InlineProcessor):
    def handleMatch(self, m, data):
        el = render_video('//www.metacafe.com/embed/{}/'.format(m.group('metacafeid')))
        return el, m.start(0), m.end(0)


class Vimeo(InlineProcessor):
    def handleMatch(self, m, data):
        el = render_video('//player.vimeo.com/video/{}'.format(m.group('vimeoid')))
        return el, m.start(0), m.end(0)


class Youtube(InlineProcessor):
    def handleMatch(self, m, data):
        el = render_video('//www.youtube.com/embed/{}'.format(m.group('youtubeid')))
        return el, m.start(0), m.end(0)


def render_video(url):
    iframe = etree.Element('iframe')
    iframe.set('src', url)
    iframe.set('allowfullscreen', 'true')
    iframe.set('frameborder', '0')
    iframe.set('class', 'youtube-iframe')
    div = etree.Element('div')
    div.set('class', 'youtube-wrapper pb-3 border-0')
    div.append(iframe)
    return div


def makeExtension(**kwargs):
    return VideoExtension(**kwargs)
