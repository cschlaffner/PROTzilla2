from django import template
from bs4 import BeautifulSoup

register = template.Library()


@register.filter
def has_element_id(field, id_name):
    soup = BeautifulSoup(field, "html.parser")
    element = soup.find(id=id_name)
    if element and element.get("id") == id_name:
        return True
    return False
