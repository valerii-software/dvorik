"""SQLite doesn't lowercase non-ASCII (e.g. Cyrillic) by default.

Register Python-level `LOWER` and `UPPER` so case-insensitive queries
across cyrillic work via Django's `Lower` / `__icontains`.
"""

from django.db.backends.signals import connection_created
from django.dispatch import receiver


@receiver(connection_created)
def install_unicode_funcs(sender, connection, **kwargs):
    if connection.vendor != 'sqlite':
        return
    raw = connection.connection
    raw.create_function('LOWER', 1, lambda s: s.lower() if s is not None else None, deterministic=True)
    raw.create_function('UPPER', 1, lambda s: s.upper() if s is not None else None, deterministic=True)
