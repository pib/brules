from brules.common import Context
from unittest import TestCase


class ContextTest(TestCase):
    def setUp(self):
        self.d = Context({'foo': 'bar', 'bar': 'baz'})

    def test_get_existing(self):
        self.assertEqual(self.d.foo, 'bar')
        self.assertEqual(self.d['bar'], 'baz')

    def test_get_nonexistant(self):
        self.assertRaises(AttributeError, getattr, self.d, 'baz')
        self.assertRaises(KeyError, self.d.__getitem__, 'baz')

    def test_set(self):
        self.d.whatever = 'yeah'
        self.assertEqual(self.d['whatever'], 'yeah')
        self.d['yeah'] = 'whatever'
        self.assertEqual(self.d.yeah, 'whatever')
