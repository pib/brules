from unittest import TestCase
from brules import Rule
from brules.helpers.basic import basic_step_set
from brules.helpers import html
from lxml.html import fromstring


class HtmlHelpersTest(TestCase):
    def setUp(self):
        self.rule = Rule()
        self.rule.add_step(html.check_tag_length)
        self.rule.add_step_set(basic_step_set)

    def test_check_tag_length_lxml(self):
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
            """
        self.rule.parse(rule_txt)
        self.rule.run(etree=fromstring(html_txt))
        self.assertEqual(self.rule.context.answers,
                         ['yes', 'yes', 'yes', 'no', 'no', 'no'])
