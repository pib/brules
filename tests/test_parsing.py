from unittest import TestCase
from brules import RuleSet, UnmatchedRuleError
from brules.rules import RegexFuncRule


class ParsingTest(TestCase):
    def setUp(self):
        self.rule_set = RuleSet()

    def _ok(self, context, args):  # pylint: disable=unused-argument
        return 'ok'

    def test_plain_text_rule(self):
        rule = RegexFuncRule("I'm a rule!", self._ok)
        self.rule_set.add_rule(rule)

        parsed = self.rule_set.parse("I'm a rule!")
        expected = [({}, rule)]
        self.assertEqual(parsed, expected)

    def test_failed_plain_text_rule(self):
        rule = RegexFuncRule("I'm a rule!", self._ok)
        self.rule_set.add_rule(rule)

        self.assertRaises(UnmatchedRuleError, self.rule_set.parse,
                          "I don't match")

    def test_plain_text_rule_suffix_content(self):
        rule = RegexFuncRule("I'm a rule", self._ok)
        self.rule_set.add_rule(rule)

        parsed = self.rule_set.parse("I'm a rule plus more")
        expected = [({'suffix_content': ' plus more'}, rule)]
        self.assertEqual(parsed, expected)

    def test_plain_text_rule_prefix_suffix_content(self):
        rule = RegexFuncRule("I'm a rule", self._ok)
        self.rule_set.add_rule(rule)

        parsed = self.rule_set.parse("Hey I'm a rule plus")
        expected = [({'prefix_content': 'Hey ', 'suffix_content': ' plus'},
                     rule)]
        self.assertEqual(parsed, expected)

    def test_regex_nocaptures(self):
        rule = RegexFuncRule('^strictly this$', self._ok)
        self.rule_set.add_rule(rule)
        parsed = self.rule_set.parse('strictly this')
        expected = [({}, rule)]
        self.assertEqual(parsed, expected)

    def test_regex_extra_fail(self):
        rule = RegexFuncRule('^strictly this$', self._ok)
        self.rule_set.add_rule(rule)
        self.assertRaises(UnmatchedRuleError, self.rule_set.parse,
                          'strictly this plus more')
        self.assertRaises(UnmatchedRuleError, self.rule_set.parse,
                          'prefix and strictly this')

    def test_regex_captures(self):
        rule = RegexFuncRule('one (?P<two>.*) three (?P<four>.*)', self._ok)
        self.rule_set.add_rule(rule)
        parsed = self.rule_set.parse('one 2 three 4\none hey three there')
        expected = [
            ({'two': '2', 'four': '4', 1: '2', 2: '4'}, rule),
            ({'two': 'hey', 'four': 'there', 1: 'hey', 2: 'there'}, rule)
        ]
        self.assertEqual(parsed, expected)

    def test_regex_numeric_captures(self):
        rule = RegexFuncRule('one (.*) three (.*)', self._ok)
        self.rule_set.add_rule(rule)
        parsed = self.rule_set.parse('one 2 three 4\none hey three there')
        expected = [
            ({1: '2', 2: '4'}, rule),
            ({1: 'hey', 2: 'there'}, rule)
        ]
        self.assertEqual(parsed, expected)

    def test_multiline(self):
        rule = RegexFuncRule('this: (.*)\nand this: (.*)', self._ok,
                             multiline=True)
        self.rule_set.add_rule(rule)
        parsed = self.rule_set.parse('this: first\nand this: second')
        expected = [({1: 'first', 2: 'second'}, rule)]
        self.assertEqual(parsed, expected)
