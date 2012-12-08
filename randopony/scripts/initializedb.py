# -*- coding: utf-8 -*-
"""RandoPony database initialization script.
"""
import os
import sys
import transaction
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )
from sqlalchemy import engine_from_config
from ..models import (
    Administrator,
    )
from ..models.meta import (
    Base,
    DBSession,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        admin = Administrator(persona_email='djl@douglatornell.ca')
        DBSession.add(admin)
