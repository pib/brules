from unittest import TestCase
from brules import RuleSet

#pylint: disable=unused-variable, unused-argument


class ConcatTest(TestCase):
    def test_concat(self):
        rs1 = RuleSet()
        rs2 = RuleSet()

        @rs1.rule('Rule 1')
        def rule1(ctx, args):
            ctx.rule1 = True

        @rs2.rule('Rule 2')
        def rule2(ctx, args):
            ctx.rule2 = True

        rs3 = rs1.concat(rs2)
        rs3.run('Rule 1\nRule 2')
        self.assertTrue(rs3.context.rule1)
        self.assertTrue(rs3.context.rule2)
