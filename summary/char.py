# coding: utf-8
import sys, re, chardet
import lxml.html
from htmlentitydefs import name2codepoint

__regx_charset   = re.compile(r'charset=(?P<charset>[\w-]+)')
__regx_reference = re.compile(u'&(#x?[0-9a-f]+|[a-z]+);', re.IGNORECASE)
__regx_num16     = re.compile(u'#x\d+', re.IGNORECASE)
__regx_num10     = re.compile(u'#\d+', re.IGNORECASE)

# detect encoding from HTML charset
def detect_charset(text):
    dom = lxml.html.fromstring(text.lower())
    # charset attr of meta
    for meta in dom.xpath('//meta[@charset]'):
        if meta.get('charset'):
            return meta.get('charset')
    return None


# charset in content attr of meta
def detect_charset_in_content(text):
    dom = lxml.html.fromstring(text.lower())
    for meta in dom.xpath('//meta[@content]'):
        encoding = __regx_charset.findall(meta.get('content'))
        if encoding:
            return encoding[0].strip()
    return None


# encoding detection corresponding to multiple formats (TEXT / HTML).
def detect_encoding(text):
    # process the text as HTML format
    encoding = detect_charset(text)
    if encoding is None:
        encoding = detect_charset_in_content(text)
    if encoding is None:
        encoding = chardet.detect(text)['encoding']
    return encoding


# decodes escaped HTML entities (&amp; lt;) to unicode
def decode_entities(text):
    ss = u''
    i  = 0
    while 1:
        m = __regx_reference.search(text, i)
        if m is None:
            ss += text[i:]
            break
        ss  += text[i:m.start()]
        i    = m.end()
        name = m.group(1)
        if name in name2codepoint.keys():
            ss += unichr(name2codepoint[name])
        elif __regx_num16.match(name):
            ss += unichr(int(u'0' + name[1:], 16))
        elif __regx_num10.match(name):
            ss += unichr(int(name[1:]))
    return ss


# unicode if input text is str
def to_unicode(text):
    if type(text) is str:
        encoding = detect_encoding(text)
        return unicode(text, encoding, 'replace')
    return text
