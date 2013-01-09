# -*- coding: utf-8 -*-
"""RandoPony-tetra celery configuration.
"""

# pragma: no cover
BROKER_URL = 'sqla+sqlite:///celery.sqlite'

CELERY_IMPORTS = (
    'randopony.views.site.populaire',
    )

# CELERY_RESULT_BACKEND = 'database'
# CELERY_RESULT_DBURI = 'sqlite:///celery.sqlite'
# CELERY_RESULT_SERIALIZER = 'json'

# CELERY_TIMEZONE = 'Canada/Pacific'
