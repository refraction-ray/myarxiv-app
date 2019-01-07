from flask_admin import Admin, AdminIndexView, expose
from flask_admin.form import SecureForm
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import abort

from .models import (db, User, Paper, UserInfo, Favorite,
                     Author)


class AccessMixIn:
    def is_accessible(self):
        if not current_user.is_authenticated:
            return False
        if not current_user.admin:
            return False
        return True

    def inaccessible_callback(self, name, **kwargs):
        # behave as there is no such page
        abort(404)


class SecuredHomeView(AccessMixIn, AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('/admin/index.html')


class myModelView(AccessMixIn, ModelView):
    can_delete = False
    form_base_class = SecureForm
    column_display_pk = True


class userModelView(myModelView):
    column_exclude_list = ['password','favorites', ]
    column_display_all_relations = True
    form_widget_args = {
        'email': {
            'readonly': True
        },
        'password': {
            'readonly': True
        }
    }


class favoriteModelView(myModelView):
    column_list = ["uid", "pid"]


class paperModelView(myModelView):
    column_searchable_list = ['arxivid', ]
    column_filters = ['id', 'arxivid']
    column_display_all_relations = True
    can_view_details = True


class authorModelView(myModelView):
    column_list = ["pid", "author", "authorrank"]
    page_size = 30
    column_searchable_list = ['author', ]



admin = Admin(index_view=SecuredHomeView(url='/admin'))

admin.add_view(userModelView(User, db.session, endpoint="admin_user", category="User"))
admin.add_view(myModelView(UserInfo, db.session, endpoint="admin_info", category="User"))
admin.add_view(paperModelView(Paper, db.session, endpoint="admin_paper", category="Paper"))
admin.add_view(authorModelView(Author, db.session, endpoint="admin_author", category="Paper"))
admin.add_view(favoriteModelView(Favorite, db.session, endpoint="admin_favorite"))
