from unittest import TestCase
from brules import StepSet
from brules.helpers.basic import basic_step_set
from brules.steps import RegexFuncStep as RFS


@RFS.make(r'Does (?P<a>.+) plus (?P<b>.+) equal (?P<c>.+)\?')
def does_a_plus_b_equal_c(context, args):
    print(args)
    if int(args.a) + int(args.b) == int(args.c):
        return True
    return False


class BasicHelpersTest(TestCase):
    def setUp(self):
        self.stepset = StepSet(does_a_plus_b_equal_c).concat(basic_step_set)

    def test_if_then_set(self):
        rules = """\
            Does 1 plus 2 equal 42?
            If so, then set answer to: Life,
                the universe,
                and everything.
            If not, then set insult to: You, sir,
              are bad at math.

            Does 2 plus 2 equal 4?
            If so, then set answer to: Ok.
             Who gave you the answer to that
             one?
            If not, then set insult to: Wow, you're so bad at math
             that you actually broke this program.
            """
        context = self.stepset.run(rules)
        self.assertEqual(context.answer,
                         'Ok. Who gave you the answer to that one?')
        self.assertEqual(context.insult,
                         'You, sir, are bad at math.')

    def test_if_then_append(self):
        rules = """\
            Does 1 plus 1 equal 2?
            If so, then append to answers: ok.
            Does 1 plus 2 equal 42?
            If so, then append to answers: Life,
                the universe,
                and everything.
            If not, then append to insults: You, sir,
              are bad at math.
            If not, then append to insults: I shall taunt you a second time!

            Does 2 plus 2 equal 4?
            If so, then append to answers: Ok.
             Who gave you the answer to that
             one?
            If not, then append to insults: Wow, you're so bad at math
             that you actually broke this program.
            """
        context = self.stepset.run(rules)
        self.assertEqual(context.answers,
                         ['ok.', 'Ok. Who gave you the answer to that one?'])
        self.assertEqual(context.insults,
                         ['You, sir, are bad at math.',
                          'I shall taunt you a second time!'])

    def test_if_then_set_yaml(self):
        rules = """\
            Does 1 plus 1 equal 2?
            If so, then set:
              math: ok-ish
              level: 1
            If not, then set:
              math: very bad
              level: -23

            Does 1 plus 2 equal 42?
            If so, then set:
              something: horribly broken
            If not, then set:
              numbers:
                - 1
                - 2
                - wait, what?
              hmm: ok
            """
        context = self.stepset.run(rules)
        self.assertEqual(context.math, 'ok-ish')
        self.assertEqual(context.level, 1)
        self.assertEqual(context.numbers, [1, 2, 'wait, what?'])
        self.assertEqual(context.hmm, 'ok')
        self.assertNotIn('something', context)
