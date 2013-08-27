from .common import UnmatchedRuleError, combined_match_dict
import re


class Rule(object):
    def parse(self, toparse, start_index):
        raise NotImplementedError('Rule subclasses must implement parse')

    def __call__(self, context, args):
        raise NotImplementedError('Rule subclasses must implement __call__')


class RegexRule(Rule):
    def __init__(self, regex, multiline=False):
        self.multiline = multiline
        self.regex = re.compile(regex)

    def parse(self, toparse, start_index):
        if self.multiline:
            return self.parse_multiline(toparse, start_index)
        else:
            return self.parse_line(toparse, start_index)

    def parse_multiline(self, toparse, start_index):
        match = self.regex.match(toparse, start_index)
        if match:
            match_dict = combined_match_dict(match)
            end = match.end()
            return (match_dict, self), end
        line = toparse[start_index:].split('\n', 1)[0]
        raise UnmatchedRuleError('Rule does not match at "{}"'.format(line))

    def parse_line(self, toparse, start_index):
        end = len(toparse)
        line_end = toparse.find('\n', start_index)
        if line_end == -1:
            line_end = end
        line = toparse[start_index:line_end]
        match = self.regex.search(line)
        if match:
            match_dict = combined_match_dict(match)

            start = match.start()
            end = match.end()

            if start > 0:
                match_dict['prefix_content'] = line[:start]
            if end < len(line):
                match_dict['suffix_content'] = line[end:]

            return (match_dict, self), line_end + 1
        raise UnmatchedRuleError('Rule does not match at "{}"'.format(line))


class RegexFuncRule(RegexRule):
    def __init__(self, regex, func, multiline=False):
        super(RegexFuncRule, self).__init__(regex, multiline)
        self.func = func

    def __call__(self, context, args):
        return self.func(context, args)
