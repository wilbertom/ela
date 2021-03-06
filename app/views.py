import calendar
import os
from flask import flash, url_for, request, current_app, jsonify
from flask_appbuilder import ModelView, BaseView, expose, has_access, RestCRUDView
from flask_appbuilder.views import expose_api, get_filter_args, make_response
from flask_appbuilder.security.decorators import permission_name, has_access_api
from flask_appbuilder.widgets import FormWidget
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.charts.views import GroupByChartView
from flask_appbuilder import SimpleFormView, MultipleView
from flask_appbuilder.models.group import aggregate_count
from flask_appbuilder.widgets import FormHorizontalWidget, FormInlineWidget, FormVerticalWidget
from flask_babel import lazy_gettext as _
from wtforms import Form, StringField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm
from werkzeug.utils import secure_filename

from app import db, appbuilder
from .models import Material, ProjectStatus, DeviceLocation, DeviceType, UserType
from .models import ElaUser, Project, Sample, Device, Experiment, File


class UserModelView(ModelView):
    datamodel = SQLAInterface(ElaUser)

    #related_views = [ProjectModelView]

    #list_columns = ['ela_users.name', 'projects.name', 'samples.name']
    #list_columns = ['usr_name']
    list_columns = ['name', 'user_type.type']

    base_order = ('name', 'asc')
    #show_fieldsets = [
    #    ('User', {'fields': ['usr_id']}),
    #    (
    #        'Personal Info',
    #        {'fields': ['files_path.path'], 'expanded': False}),
    #]

    #add_fieldsets = [
    #    ('Summary', {'fields': ['name', 'gender', 'contact_group']}),
    #    (
    #        'Personal Info',
    #        {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    #]

    #edit_fieldsets = [
    #    ('Summary', {'fields': ['name', 'gender', 'contact_group']}),
    #    (
    #        'Personal Info',
    #        {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    #]


class ProjectModelView(ModelView):
    datamodel = SQLAInterface(Project)

    related_views = [UserModelView]

    list_columns = ['name', 'proj_status.name']
    label_columns = {'name': 'Name', 'proj_status.name': 'Status'}
    base_order =('name', 'asc')
    #add_fieldsets = [
    #    ('Summary', {'fields': ['name', 'material1.name', 'proj_status.name']})

        #(
        #    'Personal Info',
        #    {'fields': ['address', 'birthday', 'personal_phone', 'personal_celphone'], 'expanded': False}),
    #]


class ProjectStatusModelView(ModelView):
    datamodel = SQLAInterface(ProjectStatus)
    list_columns = ['name']
    base_order = ('name', 'asc')

class MaterialModelView(ModelView):
    datamodel = SQLAInterface(Material)
    list_columns = ['name']
    base_order = ('name', 'asc')

class DeviceTypeModelView(ModelView):
    datamodel = SQLAInterface(DeviceType)
    list_columns = ['type']
    base_order = ('type', 'asc')

class DeviceLocationModelView(ModelView):
    datamodel = SQLAInterface(DeviceLocation)
    list_columns = ['location']
    base_order = ('location', 'asc')

class UserTypeModelView(ModelView):
    datamodel = SQLAInterface(UserType)
    list_columns = ['type']
    base_order = ('type', 'asc')

class SampleModelView(ModelView):
    datamodel = SQLAInterface(Sample)
    list_columns = ['name']
    base_order = ('name', 'asc')

class DeviceModelView(ModelView):
    datamodel = SQLAInterface(Device)
    list_columns = ['name', 'device_location.location', 'device_type.type']
    base_order = ('name', 'asc')
    label_columns = {'name': 'Name', 'device_location.location': 'Location', 'device_type.type': 'Device Type'}


class ExperimentModelView(ModelView):
    datamodel = SQLAInterface(Experiment)

    add_template = 'add_experiment.html'
    add_exclude_columns = 'files'
    label_columns = {'date_created': 'Date', 'ela_users.name': 'User', 'projects.name': 'Project', 'samples.name':'Sample', 'devices.name':'Device', 'devices.type': 'Device Type', 'file_name': 'File Name', 'download': 'Download'}
    list_columns = ['ela_user.name', 'project.name', 'samples.name','device.name', 'device.device_type.type']
    show_columns = ['file_name', 'date_created', 'download']

    @expose_api(name='create', url='/api/create', methods=['POST'])
    @has_access_api
    @permission_name('add')
    def api_create(self):
        is_valid_form = True
        get_filter_args(self._filters)
        exclude_cols = self._filters.get_relation_cols()
        form = self.add_form.refresh()

        self._fill_form_exclude_cols(exclude_cols, form)
        if form.validate():
            item = self.datamodel.obj()
            form.populate_obj(item)
            self.pre_add(item)
            if self.datamodel.add(item):
                self.post_add(item)
                http_return_code = 200
            else:
                http_return_code = 500
        else:
            is_valid_form = False
        if is_valid_form:
            response = make_response(jsonify({'message': self.datamodel.message[0],
                                              'id': item.id,
                                              'severity': self.datamodel.message[
                                                  1]}), http_return_code)
        else:
            # TODO return dict with errors
            response = make_response(jsonify({'message': 'Invalid form',
                                              'severity': 'warning'}), 500)
        return response


def pretty_month_year(value):
    return calendar.month_name[value.month] + ' ' + str(value.year)


def pretty_year(value):
    return str(value.year)


class FilesUploadView(BaseView):

    route_base = '/files'

    @staticmethod
    def get_file_size(file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    @expose('/upload/', methods=['POST'])
    def upload(self):
        # TODO: use form and force experiment_id
        experiment_id = request.form['experiment_id']

        session = self.appbuilder.get_session()

        results = []

        for file in request.files.values():
            file_name = '{}-{}'.format(
                experiment_id, secure_filename(file.filename)
            )

            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], file_name
            )

            file.save(file_path)

            db_file = File(file_name=file_name, experiment_id=experiment_id)

            session.add(db_file)
            session.commit()

            results.append({
                'name': file_name,
                'size': self.get_file_size(file),
                'type': file.mimetype,
                # 'thumbnailUrl': '',
                # 'url': '',
                # 'deleteUrl': '',
                # 'deleteType': '',
                # 'error': None,
            })

        flash('Experiment created.', 'info')

        return jsonify({'files': results})


#class HomePageView(MultipleView):
#    views = [DeviceModelView, ProjectModelView]

db.create_all()

appbuilder.add_view(UserModelView, "Users", icon="fa-envelope", category="Dictionary Tables")
appbuilder.add_view(MaterialModelView, "Materials", icon="fa-envelope", category="Dictionary Tables")
appbuilder.add_view(ProjectStatusModelView, "Project Statuses", icon="fa-envelope", category="Dictionary Tables")
appbuilder.add_view(DeviceLocationModelView, "Device Location", icon="fa-envelope", category="Dictionary Tables")
appbuilder.add_view(DeviceTypeModelView, "Device Type", icon="fa-envelope", category="Dictionary Tables")
appbuilder.add_view(UserTypeModelView, "User Type", icon="fa-envelope", category="Dictionary Tables")

appbuilder.add_view(ProjectModelView, "Projects", icon="fa-envelope", category="Projects")

appbuilder.add_view(ExperimentModelView, "Experiments", icon="fa-envelope", category="Experiments")

#appbuilder.add_separator("Main-Menu")

appbuilder.add_view(SampleModelView, "Samples", icon="fa-envelope", category="Samples")

appbuilder.add_view(DeviceModelView, "Equipment", icon="fa-envelope", category="Equipment")

appbuilder.add_view_no_menu(FilesUploadView())
# Materials will go here
# Search will go here or, better, in the top panel as a field

#appbuilder.add_view(FileDownloadView, "File Download", icon="fa-envelope", category="Data Management")

#appbuilder.add_view_no_menu(HomePageView())

appbuilder.security_cleanup()
