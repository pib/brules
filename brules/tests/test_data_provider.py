from brules.common import Context
from brules.data import Provider

from unittest import TestCase


#pylint: disable=blacklisted-name,unused-argument
class RuleTest(TestCase):
    def test_basic_subclass(self):
        class FooBarProvider(Provider):
            def __init__(self, foo='Whatever'):
                self._foo = foo

            @Provider.data_point('foo', 'Foo', 'Gives self.foo')
            def foo(self, context):
                return self._foo

            @Provider.data_point
            def bar(self, context):
                """Return context.bar"""
                return context.bar

        prov = FooBarProvider('foo value')
        self.assertEqual(prov.foo.key, 'foo')
        self.assertEqual(prov.foo.name, 'Foo')
        self.assertEqual(prov.foo.doc, 'Gives self.foo')
        self.assertEqual(prov.bar.key, 'bar')
        self.assertEqual(prov.bar.name, 'bar')
        self.assertEqual(prov.bar.doc, 'Return context.bar')
        self.assertEqual(prov.foo({}), 'foo value')
        self.assertEqual(prov.bar(Context({'bar': 'is bar'})), 'is bar')

        self.assertEqual(prov.get_data_points(),
                         {'foo': prov.foo, 'bar': prov.bar})

    def test_single_data_point(self):
        @Provider.data_point_class
        def foo():
            "Foo doc"
            return 'bar'

        self.assertEqual(foo.foo.key, 'foo')
        self.assertEqual(foo.foo.name, 'foo')
        self.assertEqual(foo.foo.doc, 'Foo doc')
        self.assertEqual(foo.foo(), 'bar')

        @Provider.data_point_class('bar', doc='Provides bar')
        def bar_provider():
            return 'bar also'

        self.assertEqual(bar_provider.bar.key, 'bar')
        self.assertEqual(bar_provider.bar.name, 'bar')
        self.assertEqual(bar_provider.bar.doc, 'Provides bar')
        self.assertEqual(bar_provider.bar(), 'bar also')
