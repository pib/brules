from unittest import TestCase
from brules import RuleSet
from brules.rules import RegexFuncRule as RFR
from textwrap import dedent
import re


class CallingTest(TestCase):
    def setUp(self):
        self.rule_set = RuleSet()

    def test_run_plaintext(self):
        def set_foo(context, args):
            self.assertEqual(args, {})
            context.foo = 'bar'
            return 'the middle'

        def set_bar(context, args):
            self.assertEqual(args, {})
            self.assertEqual(context.last_return, 'the middle')
            context.bar = 'baz'
            return 'the end'

        self.rule_set.add_rule(RFR('Set foo', set_foo))
        self.rule_set.add_rule(RFR('Set bar', set_bar))
        self.rule_set.run('Set foo\nSet bar')
        self.assertEqual(self.rule_set.context.foo, 'bar')
        self.assertEqual(self.rule_set.context.last_return, 'the end')

    def test_run_with_args(self):
        def set_x_to_y(context, args):
            context[args.x] = args.y

        def add_x_to_y(context, args):
            context.sum = int(context[args.x]) + int(context[args.y])

        def x_should_equal_y(context, args):
            self.assertEqual(str(context[args.x]), args.y)

        self.rule_set.add_rule(RFR('Set (?P<x>.*) to (?P<y>.*)', set_x_to_y))
        self.rule_set.add_rule(RFR('Add (?P<x>.*) to (?P<y>.*)', add_x_to_y))
        self.rule_set.add_rule(RFR('(?P<x>.*) should equal (?P<y>.*)',
                                   x_should_equal_y))
        self.rule_set.run(dedent("""\
            Set a to 1
            Set b to 3
            Add a to b
            sum should equal 4
            Set c to 38
            Add sum to c
            sum should equal 42"""))

    def test_run_multiline(self):
        def message(context, args):
            msg = re.sub(r'\s+', ' ', args.msg)
            messages = context.setdefault('messages', [])
            messages.append(msg)
            return msg

        rule_re = r'([ /t]*)Message:\s*(?P<msg>.*(\n\1[ \t]+.+)*)'
        self.rule_set.add_rule(RFR(rule_re, message, multiline=True))
        lines = dedent("""\
            Message: Hey there.
              This message is lots
              of lines long.
            
            Message:
              This
               is
                also
              a longer
               message.
            """)
        self.rule_set.run(lines)
        self.assertEqual(self.rule_set.context.messages,
                         ['Hey there. This message is lots of lines long.',
                          'This is also a longer message.'])
