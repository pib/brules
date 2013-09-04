from unittest import TestCase
from brules import StepSet, UnmatchedStepError
from brules.steps import RegexFuncStep


class ParsingTest(TestCase):
    def setUp(self):
        self.step_set = StepSet()

    _ok = 'NOT REALLY A FUNCTION'

    def test_plain_text_step(self):
        step = RegexFuncStep("I'm a step!", self._ok)
        self.step_set.add_step(step)

        parsed = self.step_set.parse("I'm a step!")
        expected = [({}, step)]
        self.assertEqual(parsed, expected)

    def test_failed_plain_text_step(self):
        step = RegexFuncStep("I'm a step!", self._ok)
        self.step_set.add_step(step)

        self.assertRaises(UnmatchedStepError, self.step_set.parse,
                          "I don't match")

    def test_plain_text_step_suffix_content(self):
        step = RegexFuncStep("I'm a step", self._ok)
        self.step_set.add_step(step)

        parsed = self.step_set.parse("I'm a step plus more")
        expected = [({'suffix_content': ' plus more'}, step)]
        self.assertEqual(parsed, expected)

    def test_plain_text_step_prefix_suffix_content(self):
        step = RegexFuncStep("I'm a step", self._ok)
        self.step_set.add_step(step)

        parsed = self.step_set.parse("Hey I'm a step plus")
        expected = [({'prefix_content': 'Hey ', 'suffix_content': ' plus'},
                     step)]
        self.assertEqual(parsed, expected)

    def test_regex_nocaptures(self):
        step = RegexFuncStep('^strictly this$', self._ok)
        self.step_set.add_step(step)
        parsed = self.step_set.parse('strictly this')
        expected = [({}, step)]
        self.assertEqual(parsed, expected)

    def test_regex_extra_fail(self):
        step = RegexFuncStep('^strictly this$', self._ok)
        self.step_set.add_step(step)
        self.assertRaises(UnmatchedStepError, self.step_set.parse,
                          'strictly this plus more')
        self.assertRaises(UnmatchedStepError, self.step_set.parse,
                          'prefix and strictly this')

    def test_regex_captures(self):
        step = RegexFuncStep('one (?P<two>.*) three (?P<four>.*)', self._ok)
        self.step_set.add_step(step)
        parsed = self.step_set.parse('one 2 three 4\none hey three there')
        expected = [
            ({'two': '2', 'four': '4', 1: '2', 2: '4'}, step),
            ({'two': 'hey', 'four': 'there', 1: 'hey', 2: 'there'}, step)
        ]
        self.assertEqual(parsed, expected)

    def test_regex_numeric_captures(self):
        step = RegexFuncStep('one (.*) three (.*)', self._ok)
        self.step_set.add_step(step)
        parsed = self.step_set.parse('one 2 three 4\none hey three there')
        expected = [
            ({1: '2', 2: '4'}, step),
            ({1: 'hey', 2: 'there'}, step)
        ]
        self.assertEqual(parsed, expected)

    def test_multiline(self):
        step = RegexFuncStep('this: (.*)\nand this: (.*)', self._ok,
                             multiline=True)
        self.step_set.add_step(step)
        parsed = self.step_set.parse('this: first\nand this: second')
        expected = [({1: 'first', 2: 'second'}, step)]
        self.assertEqual(parsed, expected)
