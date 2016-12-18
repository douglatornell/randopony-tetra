"""RandoPony-tetra celery configuration.
"""

# pragma: no cover
BROKER_URL = 'sqla+sqlite:///celery.sqlite'

CELERYD_CONCURRENCY = 1

CELERY_IMPORTS = (
    'randopony.views.site.brevet',
    'randopony.views.site.populaire',
)
