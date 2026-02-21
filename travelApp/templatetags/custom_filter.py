from django import template

register = template.Library()

@register.filter
def fix_party_bus_url(url):
    """Replace 'All Party Buses' with 'Party Buses' in URLs"""
    if url:
        return url.replace('All%20Party%20Buses', 'Party%20Buses').replace('All Party Buses', 'Party Buses')
    return url