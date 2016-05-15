
import os
import sys
import transaction

from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings, setup_logging
from pyramid.scripts.common import parse_vars
from cryptacular.bcrypt import BCRYPTPasswordManager as Manager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import DBSession, Entry, Base, User

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:

        manager = Manager()
        password = manager.encode('admin')

        DBSession.add(Entry(title=u'title', body=u'body'))
        DBSession.add(User(username=u'admin', password=password))

