from unittest import TestCase
from brules import RuleSet
from textwrap import dedent
import re

#pylint: disable=unused-variable


class DecoratorTest(TestCase):
    def setUp(self):
        self.rule_set = RuleSet()

    def test_rule_decorator(self):
        @self.rule_set.rule('Basic rule')
        def basic_rule(context, args):
            self.assertEqual(args, {})
            context.basic = True

        @self.rule_set.rule('Arbitrary (.*)')
        def arbitrary_x(context, args):
            context.x = args[1]
            context.arb = True

        self.rule_set.run('Basic rule\nArbitrary trout')
        self.assertEqual(self.rule_set.context.basic, True)
        self.assertEqual(self.rule_set.context.arb, True)
        self.assertEqual(self.rule_set.context.x, 'trout')

    def test_multiline_rule_decorator(self):
        @self.rule_set.multiline_rule(r'(?s)\s*"""(?P<quoted>.*?)"""')
        def triple_quotes(context, args):
            context.quoted = re.sub(r'\s+', ' ', args.quoted.strip())

        @self.rule_set.multiline_rule(r'(?s)\s*\((?P<inparens>.*?)\)')
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

        self.rule_set.run(lines)
        self.assertEqual(
            self.rule_set.context.inparens,
            'This bit here is in parens. """ This bit is still in '
            'parens, despite the fact that it is also in quotes. """')
        self.assertEqual(self.rule_set.context.quoted,
                         'This bit here, however, is in quotes')
