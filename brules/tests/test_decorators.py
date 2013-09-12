from unittest import TestCase
from brules import StepSet
from textwrap import dedent
import re

#pylint: disable=unused-variable


class DecoratorTest(TestCase):
    def setUp(self):
        self.step_set = StepSet()

    def test_step_decorator(self):
        @self.step_set.step('Basic step')
        def basic_step(context, args):
            self.assertEqual(args, {})
            context.basic = True

        @self.step_set.step('Arbitrary (.*)')
        def arbitrary_x(context, args):
            context.x = args[1]
            context.arb = True

        self.step_set.run('Basic step\nArbitrary trout')
        self.assertEqual(self.step_set.context.basic, True)
        self.assertEqual(self.step_set.context.arb, True)
        self.assertEqual(self.step_set.context.x, 'trout')

    def test_multiline_step_decorator(self):
        @self.step_set.multiline_step(r'(?s)\s*"""(?P<quoted>.*?)"""')
        def triple_quotes(context, args):
            context.quoted = re.sub(r'\s+', ' ', args.quoted.strip())

        @self.step_set.multiline_step(r'(?s)\s*\((?P<inparens>.*?)\)')
        def parens(context, args):
            context.inparens = re.sub(r'\s+', ' ', args.inparens.strip())

        lines = dedent('''\
            (This bit here
             is in parens.
             """ This bit is still in parens,
                 despite the fact that it is
                 also in quotes.
             """) """ This bit here, however,
                      is in quotes """
            ''')

        self.step_set.run(lines)
        self.assertEqual(
            self.step_set.context.inparens,
            'This bit here is in parens. """ This bit is still in '
            'parens, despite the fact that it is also in quotes. """')
        self.assertEqual(self.step_set.context.quoted,
                         'This bit here, however, is in quotes')
