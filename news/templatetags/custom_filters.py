from django import template

register = template.Library()


@register.filter(name='censor')
def censor(value):
    cens_words = ['word1', 'word2']
    text = set(value.split())
    for i in text:
        for j in cens_words:
            if i == j:
                return value.replace(i, '*' * len(i))
    return value

