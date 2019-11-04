from django import template

register = template.Library()

def is_menu_active(slug, menu):
    if slug == menu:
        return 'is-active'
    else:
        return ''

register.filter('menu_active', is_menu_active)
