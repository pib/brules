from unittest import TestCase
from brules import StepSet
from brules.helpers.basic import if_then_set
from brules.helpers import html


class HtmlHelpersTest(TestCase):
    def setUp(self):
        self.stepset = StepSet()
        self.stepset.add_step(html.check_tag_length)
        self.stepset.add_step(if_then_set)

    def test_check_tag_length_lxml(self):
        html_txt = """
            <html>
              <head>
                <title>This is the title, yo.</title>
              </head>
              <body></body>
            </html>
            """
        rules = """\
            Does the title tag have less than 60 characters?
            If so, then set ok to: yes
            If not, then set ok to: no
            """
        
