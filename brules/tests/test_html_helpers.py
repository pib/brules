from unittest import TestCase
from brules import Rule
from brules.helpers.basic import basic_step_set
from brules.helpers.html import html_step_set
from lxml.html import fromstring


class HtmlHelpersTest(TestCase):
    def setUp(self):
        self.rule = Rule()
        self.rule.add_step_set(html_step_set)
        self.rule.add_step_set(basic_step_set)

    def test_check_tag_exists(self):
        html1 = """
            <html><head><title>This is the title, yo.</title></head></html>
            """
        html2 = """<html><head></head><body><h1>YO</h1></body></html>"""
        rule_txt = """\
            Does the page have a title tag?
            If so, then set title to: yes
            If not, then set title to: no

            Does the page have an h1 tag?
            If so, then set h1 to: yes
            If not, then set h1 to: no
            """
        self.rule.parse(rule_txt)
        self.rule.run(etree=fromstring(html1))
        self.assertEquals(self.rule.context.title, 'yes')
        self.assertEquals(self.rule.context.h1, 'no')
        self.rule.run(etree=fromstring(html2))
        self.assertEquals(self.rule.context.title, 'no')
        self.assertEquals(self.rule.context.h1, 'yes')

    def test_check_tag_length(self):
        html_txt = """
            <html>
              <head>
                <title>This is the title, yo.</title>
              </head>
              <body><span>Hello!</span><b></b>
                <div>Some more words!</div></body>
            </html>
            """
        rule_txt = """\
            Does the title tag have less than 60 characters?
            If so, then append to answers: yes
            If not, then append to answers: no

            Does the title tag have more than 10 characters?
            If so, then append to answers: yes
            If not, then append to answers: no

            Does the title tag have less than 10 words?
            If so, then append to answers: yes
            If not, then append to answers: no

            Does the body tag have more than 4 words?
            If so, then append to answers: yes
            If not, then append to answers: no

            Does the body tag have less than 4 words?
            If so, then append to answers: yes
            If not, then append to answers: no

            Does the b tag have more than 4 words?
            If so, then append to answers: yes
            If not, then append to answers: no

            Does the nonexistant tag have more than 3 words?
            If so, then append to answers: yes
            If not, then append to answers: no
            """
        self.rule.parse(rule_txt)
        self.rule.run(etree=fromstring(html_txt))
        self.assertEqual(self.rule.context.answers,
                         ['yes', 'yes', 'yes', 'no', 'no', 'no', 'no'])

    def test_given_tag_with_attr(self):
        html = '<html><a></a><a href="foo.html">Foo</a></html>'
        rule = ('Given the a tag with the attribute href=foo.html\n'
                'Does the href attribute have less than 20 characters?')
        rule2 = ('Given the a tag with the attribute href=foo.html\n'
                 'Does the nope attribute have less than 20 characters?')

        self.rule.parse(rule)
        self.rule.run(etree=fromstring(html))
        self.assertEquals(self.rule.context.referenced_elements[0].tag, 'a')
        self.assertEquals(self.rule.context.referenced_elements[0].text, 'Foo')
        self.assertEquals(self.rule.context.last_return, True)

        self.rule.parse(rule2)
        self.rule.run(etree=fromstring(html))
        self.assertEquals(self.rule.context.referenced_elements[0].text, 'Foo')
        self.assertEquals(self.rule.context.last_return, True)

    def test_all_tag_have_atr(self):
        html = '''\
            <html><body>
                <a href="/foo" class="a">foo</a><a class="b">noop</a>
            </body></html>'''
        rule = '''\
            Do all the a tags have an href attribute?
            If so, then set hrefs to: yes
            If not, then set hrefs to: no
            Do all the a tags have a class attribute?
            If so, then set classes to: yes
            If not, then set classes to: no
        '''

        self.rule.parse(rule)
        self.rule.run(etree=fromstring(html))
        self.assertEqual(self.rule.context.hrefs, 'no')
        self.assertEqual(self.rule.context.classes, 'yes')
