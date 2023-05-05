from django.conf import settings

import distinctipy


def get_hex_colors(n: int, factor: float = 0.3) -> list[str]:
    """
    Get N distinct hex colors
    """
    return [distinctipy.distinctipy.get_hex(i) for i in distinctipy.get_colors(n, pastel_factor=factor)]


def settings_ctx(request):
    return {'settings': settings}