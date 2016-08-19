from wtforms import Form, StringField, FileField, SubmitField
from wtforms.validators import DataRequired
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm


class MyForm(DynamicForm):
    field1 = StringField(('Field1'),
        description=('Your field number one!'),
        validators = [DataRequired()], widget=BS3TextFieldWidget())
    field2 = StringField(('Field2'),
        description=('Your field number two!'), widget=BS3TextFieldWidget())


class UploadFiles(DynamicForm):

    comment = StringField(('Comment'))
    files = FileField('Select Dataset Files', render_kw={'multiple': True})
        #'Select Dataset Files',
        #render_kw={'multiple': True},
    #)
    upload = SubmitField('Upload Now!')
