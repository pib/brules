from .steps import RegexStep
import re

offside_rule = r'\s*(?P<body>.*(\n\1[ \t]+.+)*)'


class IfThenSet(RegexStep):
    """ Sets a variable to a given (optionally multiline) string,
    based on the return value of the previously run rule. Returns that
    same return value so multiple instances can be chained
    together. Trims whitespace from either end of the string and
    compresses all other whitespace into single spaces.

    If a multiline string is used, the following lines must be
    indented more than the first line. For example:

        Is it Tuesday?
        If so, then set foo to: Line One.
          Line two.
          Line Three
        If not, then set bar to: This example continues.
         It continues to continue on this line.
          And this one.
    """
    def __init__(self):
        regex = 'If (?P<mod>so|not), then set (?P<name>.*) to:' + offside_rule
        super(IfThenSet, self).__init__(regex, multiline=True)

    def __call__(self, context, args):
        if (args.mod == 'so' and context.last_return) \
                or (args.mod == 'not' and not context.last_return):
            body = re.sub(r'\s+', ' ', args.body.strip())
            context[args.name] = body
        return context.last_return
