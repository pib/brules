from ..steps import RegexFuncStep
from ..stepset import StepSet
import logging
import re

log = logging.getLogger(__name__)

offside_rule = r'[ /t]*(?P<body>.*(\n\1[ \t]+.+)*)'


@RegexFuncStep.make(r'([ \t]*)If (?P<mod>so|not), then set (?P<name>.*) to:'
                    + offside_rule, multiline=True)
def if_then_set(context, args):
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
    if (args.mod == 'so' and context.last_return) \
            or (args.mod == 'not' and not context.last_return):
        body = re.sub(r'\s+', ' ', args.body.strip())
        log.debug('setting "%s" to "%s"', args.name, body)
        context[args.name] = body
    else:
        log.debug('not setting "%s" to "%s"', args.name, body)
    return context.last_return


@RegexFuncStep.make(r'([ \t]*)If (?P<mod>so|not), then append to (?P<name>.*):'
                    + offside_rule, multiline=True)
def if_then_append(context, args):
    """ Like if_then_set, but builds up a list instead of setting a
    single variable
    """
    if (args.mod == 'so' and context.last_return) \
            or (args.mod == 'not' and not context.last_return):
        body = re.sub(r'\s+', ' ', args.body.strip())
        log.debug('appending "%s" to "%s"'.format(body, args.name))
        context.setdefault(args.name, []).append(body)
    else:
        log.debug('not appending "{}" to "{}"'.format(args.body, args.name))
    return context.last_return

basic_step_set = StepSet(if_then_set, if_then_append)
