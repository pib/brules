from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from future import standard_library
from future.builtins import *

from brules import Context
from brules.rules import Rule
from brules.helpers.basic import basic_step_set
from brules.helpers.html import html_step_set

from argparse import ArgumentParser
from lxml.html import fromstring
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

from importlib import import_module
import json
import logging
import textwrap

log = logging.getLogger(__name__)


def run():
    import sys
    main(sys.argv[1:])


def main(argv):
    parser = ArgumentParser(description='Run some rules on a webpage')
    parser.add_argument('url')
    parser.add_argument('-d', '--dir', default='rules', required=False)
    parser.add_argument('-D', '--debug', default=False, action='store_true')
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument('-s', '--extra-stepset', default=None,
                        help="i.e. package.mod:step_set")
    parser.add_argument('-c', '--context-factory', default=None,
                        help="i.e. package.mod:ContextSubclass")
    parser.add_argument('-o', '--output', default='brule_output.json')
    args = parser.parse_args(argv)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    etree = load_url(args.url)
    ctx_class = (load_mod_var(args.context_factory)
                 if args.context_factory else Context)

    context = ctx_class(etree=etree, url=args.url)
    rules = load_rules(args.dir, args.extra_stepset, context)
    run_rules(rules)
    print_results(rules, args.verbose)
    write_results(rules, args.output)


def load_rules(rule_dir, extra_stepset, context):
    base_rule = Rule()
    base_rule.context = context
    if extra_stepset:
        base_rule.add_step_set(load_mod_var(extra_stepset))
    base_rule.add_step_set(basic_step_set)
    base_rule.add_step_set(html_step_set)
    return base_rule.load_directory(rule_dir)


def load_mod_var(var_path):
    mod_name, var_name = var_path.split(':')
    mod = import_module(mod_name)
    return getattr(mod, var_name)


def load_url(url):
    log.debug('Loading %s', url)
    req = urlopen(url)
    if req.geturl() != url:
        log.debug('Redirected to %s', req.geturl())
    return fromstring(req.read())


def run_rules(rules):
    for rule in rules:
        rule.run()


def print_results(rules, verbose):
    for rule in rules:
        status = 'Rule: {} ({})'.format(
            rule.metadata.get('name', rule.file_path),
            rule.metadata.get('id', rule.file_path))
        status = red(status) if rule.context.get('fail') else green(status)
        print(status)
        if verbose or rule.context.get('fail'):
            keylen = max(len(str(k)) for k in rule.context) + 1
            for k, v in list(rule.context.items()):
                try:
                    v = v.format_map(rule.context)
                except:
                    pass
                indent = ' ' * (keylen + 4)
                if isinstance(v, list):
                    v = ', '.join([str(i).replace(' ', '\a')
                                  for i in v])
                    v = '[' + v + ']'
                    indent = indent + ' '

                out = '{}: {}'.format(str(k).ljust(keylen), v)
                out = textwrap.fill(out, 80, initial_indent='  ',
                                    subsequent_indent=indent)
                print(out.replace('\a', ' '))


def write_results(rules, output):
    result = [{'metadata': r.metadata, 'context': r.context} for r in rules]
    with open(output, 'w') as f:
        json.dump(result, f, cls=LaxEncoder)


class LaxEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return repr(obj)


def red(txt):
    return '\033[91m' + txt + '\033[0m'


def green(txt):
    return '\033[92m' + txt + '\033[0m'

if __name__ == '__main__':
    run()
