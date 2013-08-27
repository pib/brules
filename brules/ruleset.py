from .common import AttrDict, UnmatchedRuleError, combined_match_dict
from .rules import RegexFuncRule


class RuleSet(object):
    def __init__(self):
        self.context = AttrDict()
        self._rules = []
        self._multiline_rules = []

    def run(self, step_text):
        steps = self.parse(step_text)
        for args, rule in steps:
            self.context['last_return'] = rule(self.context, args)

    def concat(self, other):
        new_rs = RuleSet()
        for name in '_rules', '_multiline_rules':
            new_list = getattr(self, name) + getattr(other, name)
            setattr(new_rs, name, new_list)

        return new_rs

    def rule(self, pattern):
        def attach_rule(f):
            rule = RegexFuncRule(pattern, f)
            self.add_rule(rule)
            return f
        return attach_rule

    def multiline_rule(self, pattern):
        def attach_multiline_rule(f):
            rule = RegexFuncRule(pattern, f, multiline=True)
            self.add_rule(rule)
            return f
        return attach_multiline_rule

    def add_rule(self, rule):
        self._rules.append(rule)

    def parse(self, toparse):
        matches = []
        i = 0
        end = len(toparse)
        while i < end:
            match_found = False
            for rule in self._rules:
                try:
                    match, i = rule.parse(toparse, i)
                    matches.append(match)
                    match_found = True
                except UnmatchedRuleError:
                    continue
            if not match_found:
                line = toparse[i:].split('\n', 1)[0]
                if line.strip() == '':
                    i += len(line) + 1
                    continue
                raise UnmatchedRuleError(
                    'No matching rules for "{}"'.format(line))
        return matches
