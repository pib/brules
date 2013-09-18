from ..steps import RegexFuncStep
from ..stepset import StepSet

attr = r'(?P<attr>\w+)'
val = r'(?P<val>.+)'
tag = r'(?P<tag>\w+)'
name = r'(?P<name>\w+)'
tag_attr = r'(?P<tag_attr>tag|attribute)'
less_more = '(?P<less_more>less|more)'
length = r'(?P<length>\d+)'
chars_words = '(?P<chars_words>characters|words)'


@RegexFuncStep.make(r'Does the page have a[n]? {} tag\?'.format(tag))
def check_tag_exists(context, args):
    # Does the page have a title tag?
    tag = context.etree.find('.//' + args.tag)
    if tag is not None:
        context.referenced_elements = [tag]
        return True
    else:
        return False


@RegexFuncStep.make(r'Does the {} {} have {} than {} {}\?'.format(
    name, tag_attr, less_more, length, chars_words))
def check_tag_length(context, args):
    if args.tag_attr == 'attribute':
        # Does the content attribute have less than 160 characters?
        try:
            txt = context.referenced_elements[0].attrib[args.name]
        except (AttributeError, KeyError):
            txt = ''
    else:
        # Does the title tag have less than 60 characters?
        elem = context.etree.find('.//' + args.name)
        if elem is not None:
            context.referenced_elements = [elem]
            txt = elem.text_content()
        else:
            txt = ''

    if args.chars_words == 'characters':
        tag_length = len(txt)
    elif args.chars_words == 'words':
        tag_length = len(txt.strip().split())

    if args.less_more == 'less':
        return tag_length < int(args.length)
    elif args.less_more == 'more':
        return tag_length > int(args.length)


@RegexFuncStep.make(r'Given the {} tag with the attribute {}={}'.format(
    tag, attr, val))
def given_tag_attr(context, args):
    elem = context.etree.find('.//{}[@{}="{}"]'.format(args.tag,
                                                       args.attr,
                                                       args.val))
    context.referenced_elements = [elem]


@RegexFuncStep.make(r'Do all the {} tags have a[n]? {} attribute\?'.format(
    tag, attr))
def all_tags_have_attr(context, args):
    tags = context.etree.xpath('.//{}[not(string(@{}))]'.format(args.tag,
                                                                args.attr))
    if len(tags):
        context.referenced_elements = tags
        return False
    else:
        return True


html_step_set = StepSet(check_tag_exists, check_tag_length, given_tag_attr,
                        all_tags_have_attr)
