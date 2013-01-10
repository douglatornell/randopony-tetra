# -*- coding: utf-8 -*-
"""RandoPony-tetra celery configuration.
"""

# pragma: no cover
BROKER_URL = 'sqla+sqlite:///celery.sqlite'

CELERY_IMPORTS = (
    'randopony.views.site.populaire',
    )
