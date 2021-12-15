from datetime import datetime

import flask_admin as admin
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_admin import expose
from flask_admin import helpers
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from peewee import DoesNotExist
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from afpy.forms.auth import ChangePasswordForm
from afpy.forms.auth import LoginForm
from afpy.forms.auth import RegistrationForm
from afpy.models.AdminUser import AdminUser
from afpy.models.JobPost import JobPost
from afpy.models.NewsEntry import NewsEntry


# Create customized index view class that handles login & registration
class AdminIndexView(admin.AdminIndexView):
    @expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(AdminIndexView, self).index()

    @expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            try:
                user = AdminUser.get(AdminUser.email == form.email_or_username.data)
            except DoesNotExist:
                user = AdminUser.get(AdminUser.username == form.email_or_username.data)
            if check_password_hash(user.password, form.password.data):
                login_user(user)
            else:
                flash("Incorrect username or password")

        if current_user.is_authenticated:
            return redirect(url_for("admin.index"))
        self._template_args["form"] = form
        return super(AdminIndexView, self).index()

    @expose("/logout/")
    def logout_view(self):
        logout_user()
        return redirect(url_for("admin.index"))


class NewAdminView(admin.BaseView):
    @expose("/", methods=("GET", "POST"))
    def register_view(self):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.index"))
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            AdminUser.create(
                email=form.email.data,
                username=form.username.data,
                password=generate_password_hash(form.password.data),
                dt_added=datetime.now(),
            ).save()
            return redirect(url_for("admin.index"))
        return self.render("admin/create_user.html", form=form)


class ChangePasswordView(admin.BaseView):
    @expose("/", methods=("GET", "POST"))
    def change_password_view(self):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.index"))
        form = ChangePasswordForm(request.form)
        if helpers.validate_form_on_submit(form):
            if not check_password_hash(current_user.password, form.old_password.data):
                flash("Incorrect old password.")
                return self.render("admin/change_password.html", form=form)
            if not form.new_password.data == form.new_password_confirmation.data:
                flash("Passwords don't match.")
                return self.render("admin/change_password.html", form=form)
            current_user.password = generate_password_hash(form.new_password.data)
            current_user.save()
            return redirect(url_for("admin.index"))
        return self.render("admin/change_password.html", form=form)


class _ModerateView(admin.BaseView):
    model = None

    @expose("/", methods=["GET"])
    def moderate_view(self):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.index"))
        items = self.model.select().where(self.model.state == "waiting").order_by(self.model.dt_submitted.desc())
        return self.render("admin/moderate_view.html", items=items, edit_view=self.edit_view)

    @expose("/preview/<id>", methods=["GET"])
    def preview_item(self, id):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.index"))
        item = self.model.get_by_id(id)
        return self.render("pages/post.html", post=item, preview=True)

    @expose("/moderate/action/<id>/<action>", methods=["GET"])
    def moderate_action(self, id, action):
        if not current_user.is_authenticated:
            return redirect(url_for("admin.index"))
        item = self.model.get_by_id(id)
        if action == "approve":
            item.state = "published"
            item.approved_by = current_user.id
            item.dt_published = datetime.now()
            item.save()
        elif action == "reject":
            item.state = "rejected"
            item.approved_by = current_user.id
            item.save()
        else:
            flash("Wrong action type")
            return redirect(url_for("admin.index"))
        return redirect(url_for(".moderate_view"))


class JobsModerateView(_ModerateView):
    model = JobPost
    edit_view = "jobpost.edit_view"


class NewsModerateView(_ModerateView):
    model = NewsEntry
    edit_view = "newsentry.edit_view"


class CustomFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated
