from brules.common import Context
from brules.data import Provider
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

    def test_data_provider(self):
        """ Context will pull missing attributes from the data
        provider and cache them within its own data.
        """
        class AbcProvider(Provider):
            def __init__(self, a, b, c):
                self._a = a
                self._b = b
                self._c = c

            @Provider.data_point
            def a(self, context):
                return self._a

            @Provider.data_point
            def ab(self, context):
                return context.a + self._b

            @Provider.data_point
            def abc(self, context):
                return context.ab + self._c

        c = Context()
        c.data_provider = AbcProvider('A', 'b', 'C')

        self.assertEqual(c.abc, 'AbC')

        c.data_provider = None
        self.assertEqual(c.a, 'A')
        self.assertEqual(c.ab, 'Ab')
        self.assertEqual(c.abc, 'AbC')
        del c['ab']
        self.assertNotIn('ab', c)
        self.assertEqual(len(c), 2)
