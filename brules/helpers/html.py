from ..steps import RegexFuncStep

tag = r'(?P<tag>\w+)'
less_more = '(?P<less_more>less|more)'
length = r'(?P<length>\d+)'
chars_words = '(?P<chars_words>characters|words)'


@RegexFuncStep.make(r'Does the {} tag have {} than {} {}?'.format(
    tag, less_more, length, chars_words))
def check_tag_length(context, args):
    # Does the title tag have less than 60 characters?
    tag = context.etree.find('.//' + args.tag)

    if args.chars_words == 'characters':
        tag_length = len(tag.text)
    elif args.chars_words == 'words':
        tag_length = len(tag.text_content().strip().split())

    if args.less_more == 'less':
        return tag_length < int(args.length)
    elif args.less_more == 'more':
        return tag_length > int(args.length)
