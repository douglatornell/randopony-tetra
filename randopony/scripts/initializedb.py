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
    EmailAddress,
    Link,
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
    # Deployment specific initialization
    admin = Administrator(persona_email='djl@douglatornell.ca')
    admin_email = EmailAddress(key='admin_email', email='djl@douglatornell.ca')
    entry_form_url = Link(
        key='entry_form',
        url='http://www.randonneurs.bc.ca/organize/eventform.pdf')
    with transaction.manager:
        DBSession.add(admin)
        DBSession.add(admin_email)
        DBSession.add(entry_form_url)
