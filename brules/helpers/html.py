from ..steps import RegexFuncStep

tag = r'(?P<tag>\w+)'
less_more = '(?P<less_more>less|more)'
length = r'(?P<length>\d+)'
chars_words = '(?P<chars_words>characters|words)'


@RegexFuncStep.make(r'Does the {} tag have {} than {} {}?'.format(
    tag, less_more, length, chars_words))
def check_tag_length(context, args):
    pass
