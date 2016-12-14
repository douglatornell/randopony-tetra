from pyramid.paster import get_app, setup_logging

# Load Sentry DSN into environment from private file
exec(open('/home/bcrandonneur/webapps/randopony_py3/randopony-tetra/randopony/sentry_dsn.py').read())

ini_path = '/home/bcrandonneur/webapps/randopony_py3/randopony-tetra/production.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main')
