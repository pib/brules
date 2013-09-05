from unittest import TestCase
from brules.common import u
from future.utils.six import text_type


class CommonTest(TestCase):
    def test_u(self):
        self.assertIsInstance(u(b'hello'), text_type)
        self.assertIsInstance(u('hello'), text_type)
        self.assertIsInstance(u(u'hello'), text_type)
