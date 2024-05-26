from django import template


register = template.Library()


@register.filter()
def remove_page_param(value):
    if 'page' in value:
        del value['page']
    return value


#remove_page_param_tag = register.simple_tag(remove_page_param)
