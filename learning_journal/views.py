import datetime

from pyramid.exceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import forget, remember, authenticated_userid
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .forms import (
    EntryCreateForm,
    LoginForm,
    )

from .models import (
    DBSession,
    Entry,
    User,
    )

@view_config(route_name='home', renderer='templates/list.jinja2')
def index_page(request):
    entries = Entry.all()
    form = None
    if not authenticated_userid(request):
        form = LoginForm()
    return {'entries': entries, 'login_form': form}


@view_config(route_name='detail', renderer='templates/detail.jinja2')
def blog_view(request):
    this_id = request.matchdict.get('id', -1)
    entry = Entry.by_id(this_id)
    if not entry:
        return HTTPNotFound()
    return {'entry': entry}


@view_config(route_name='action', match_param='action=create', renderer='templates/edit.jinja2', permission='create')
def create(request):
    entry = Entry()
    form = EntryCreateForm(request.POST)
    if request.method == 'POST' and form.validate():
        form.populate_obj(entry)
        DBSession.add(entry)
        return HTTPFound(location=request.route_url('home'))
    return {'form': form, 'action': 'create'}


@view_config(route_name='action', match_param='action=update', renderer='templates/edit.jinja2', permission='edit')
def update(request):
    this_id = request.GET['id']
    entry = Entry.by_id(this_id)
    form = EntryCreateForm(request.POST, title=entry.title, body=entry.body)
    if request.method == 'POST' and form.validate():
        form.populate_obj(entry)
        entry.edited = datetime.datetime.utcnow()
        DBSession.add(entry)
        return HTTPFound(location=request.route_url('detail', id=this_id))
    return {'form': form, 'action': 'update'}


@view_config(route_name='auth', match_param='action=in', renderer='string', request_method='POST')
def sign_in(request):
    login_form = None
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
    if login_form and login_form.validate():
        user = User.by_name(login_form.username.data)
        if user and user.verify_password(login_form.password.data):
            headers = remember(request, user.username)
        else:
            headers = forget(request)
    else:
        headers = forget(request)
    return HTTPFound(location=request.route_url('home'), headers=headers)

