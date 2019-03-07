"""RandoPony database initialization script.
"""
import os
import sys

from passlib.apps import custom_app_context
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)
from sqlalchemy import engine_from_config
import transaction

from randopony.models import (
    Administrator,
    EmailAddress,
    Link,
)
from randopony.models.meta import (
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
    password1, password2 = True, False
    while password1 != password2:
        password1 = input('password for administrator djl@douglatornell.ca: ')
        password2 = input('again: ')
    password_hash = custom_app_context.encrypt(password1)
    admin = Administrator(
        email='djl@douglatornell.ca',
        password_hash=password_hash,
    )
    admin_email = EmailAddress(
        key='admin_email',
        email='djl@douglatornell.ca',
    )
    from_randopony = EmailAddress(
        key='from_randopony',
        email='randopony@randonneurs.bc.ca',
    )
    club_webmaster = EmailAddress(
        key='club_webmaster',
        email='gowlin@gmail.com',
    )
    entry_form_url = Link(
        key='entry_form',
        url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
    )
    results_link = Link(
        key='results_link',
        url='https://database.randonneurs.bc.ca/browse/randonnees',
    )
    is_club_member_api = Link(
        key='is_club_member_api',
        url='https://database.randonneurs.bc.ca/api/member/'
            '{last_name}/{first_name}/status/',
    )
    membership_link = Link(
        key='membership_link',
        url='https://ccnbikes.com/#!/events/bc-randonneurs-cycling-club-membership-2019',
    )
    with transaction.manager:
        DBSession.add_all((
            admin,
            admin_email,
            from_randopony,
            club_webmaster,
            entry_form_url,
            results_link,
            is_club_member_api,
            membership_link,
        ))


if __name__ == '__main__':
    main()
