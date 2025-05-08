from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplie deux valeurs décimales"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return ''

@register.filter
def subtract(value, arg):
    """Soustrait deux valeurs décimales"""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError):
        return '' 