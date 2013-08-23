from unittest import TestCase
from brules import RuleSet, UnmatchedRuleError


class ParsingTest(TestCase):
    def setUp(self):
        self.rule_set = RuleSet()

    def _ok(self, context):
        return 'ok'

    def test_plain_text_rule(self):
        self.rule_set.add_rule("I'm a rule!", self._ok)

        parsed = self.rule_set.parse("I'm a rule!")
        expected = [({}, self._ok)]
        self.assertEqual(parsed, expected)

    def test_failed_plain_text_rule(self):
        self.rule_set.add_rule("I'm a rule!", self._ok)

        self.assertRaises(UnmatchedRuleError, self.rule_set.parse,
                          "I don't match")

    def test_plain_text_rule_suffix_content(self):
        self.rule_set.add_rule("I'm a rule", self._ok)

        parsed = self.rule_set.parse("I'm a rule plus more")
        expected = [({'suffix_content': ' plus more'}, self._ok)]
        self.assertEqual(parsed, expected)

    def test_plain_text_rule_prefix_suffix_content(self):
        self.rule_set.add_rule("I'm a rule", self._ok)

        parsed = self.rule_set.parse("Hey I'm a rule plus")
        expected = [({'prefix_content': 'Hey ', 'suffix_content': ' plus'},
                     self._ok)]
        self.assertEqual(parsed, expected)

    def test_regex_nocaptures(self):
        self.rule_set.add_rule('^strictly this$', self._ok)
        parsed = self.rule_set.parse('strictly this')
        expected = [({}, self._ok)]
        self.assertEqual(parsed, expected)

    def test_regex_extra_fail(self):
        self.rule_set.add_rule('^strictly this$', self._ok)
        self.assertRaises(UnmatchedRuleError, self.rule_set.parse,
                          'strictly this plus more')
        self.assertRaises(UnmatchedRuleError, self.rule_set.parse,
                          'prefix and strictly this')

    def test_regex_captures(self):
        self.rule_set.add_rule('one (?P<two>.*) three (?P<four>.*)', self._ok)
        parsed = self.rule_set.parse('one 2 three 4\none hey three there')
        expected = [
            ({'two': '2', 'four': '4', 1: '2', 2: '4'}, self._ok),
            ({'two': 'hey', 'four': 'there', 1: 'hey', 2: 'there'}, self._ok)
        ]
        self.assertEqual(parsed, expected)

    def test_regex_numeric_captures(self):
        self.rule_set.add_rule('one (.*) three (.*)', self._ok)
        parsed = self.rule_set.parse('one 2 three 4\none hey three there')
        expected = [
            ({1: '2', 2: '4'}, self._ok),
            ({1: 'hey', 2: 'there'}, self._ok)
        ]
        self.assertEqual(parsed, expected)

    def test_multiline(self):
        self.rule_set.add_multiline_rule('this: (.*)\nand this: (.*)',
                                         self._ok)
        parsed = self.rule_set.parse('this: first\nand this: second')
        expected = [({1: 'first', 2: 'second'}, self._ok)]
        self.assertEqual(parsed, expected)
