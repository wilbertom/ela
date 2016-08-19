# coding: utf-8

import datetime
from flask import Markup, url_for
from flask_appbuilder.models.mixins import AuditMixin, FileColumn
from flask_appbuilder import Model
from flask_appbuilder.filemanager import get_file_original_name
from sqlalchemy.dialects import postgresql

from sqlalchemy import Table, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.schema import FetchedValue, Sequence
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy


mindate = datetime.date(datetime.MINYEAR, 1, 1)


class DeviceLocation(Model):
    __tablename__ = 'device_location'

    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(45), nullable=False)

    def __repr__(self):
      return self.location


class DeviceType(Model):
    __tablename__ = 'device_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(45), nullable=False)

    def __repr__(self):
      return self.type


class Device(Model):
    __tablename__ = 'devices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    type = Column(ForeignKey(u'device_type.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)
    location = Column(ForeignKey(u'device_location.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)

    device_location = relationship(u'DeviceLocation', primaryjoin='Device.location == DeviceLocation.id', backref=u'devices')
    device_type = relationship(u'DeviceType', primaryjoin='Device.type == DeviceType.id', backref=u'devices')

    def __repr__(self):
      return self.name


class ElaUser(Model):
    __tablename__ = 'ela_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)
    type = Column(ForeignKey(u'user_type.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)

    user_type = relationship(u'UserType', primaryjoin='ElaUser.type == UserType.id', backref=u'ela_users')

    def __repr__(self):
      return self.name


assoc_users_projects = Table('users_projects', Model.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('user_id', Integer, ForeignKey('ela_users.id')),
                           Column('project_id', Integer, ForeignKey('projects.id', ondelete=u'SET NULL'))
)


class Experiment(Model):
    __tablename__ = 'experiments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(ForeignKey(u'projects.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)
    device_id = Column(ForeignKey(u'devices.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)
    ela_user_id = Column(ForeignKey(u'ela_users.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)
    sample_id = Column(ForeignKey(u'samples.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)
    date_created = Column(DateTime, server_default=FetchedValue())

    project = relationship(u'Project', primaryjoin='Experiment.project_id == Project.id', backref=u'experiments')
    device = relationship(u'Device', primaryjoin='Experiment.device_id == Device.id', backref=u'experiments')
    ela_user = relationship(u'ElaUser', primaryjoin='Experiment.ela_user_id == ElaUser.id', backref=u'experiments')
    samples = relationship(u'Sample', primaryjoin='Experiment.sample_id == Sample.id', backref=u'experiment')

    def __repr__(self):
      return 'Experiment by {} on {}'.format(self.ela_user.name, self.date_created)


class File(Model):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(ForeignKey(u'experiments.id'), nullable=False)
    file_name = Column(String(250), nullable=False)

    experiment = relationship(u'Experiment', primaryjoin='File.experiment_id == Experiment.id', backref=u'files')

    def download(self):
        return Markup('<a href="' + url_for('ExperimentModelView.download', filename=str(self.file_name)) + '">Download</a>')

    # def file_name(self):
    #     return get_file_original_name(str(self.file_name))


class Material(Model):
    __tablename__ = 'materials'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)

    def __repr__(self):
      return self.name


class ProjectStatus(Model):
    __tablename__ = 'proj_status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), nullable=False)

    def __repr__(self):
      return self.name

'''
assoc_project_sample = Table('project_sample', Model.metadata,
                             Column('id', Integer, primary_key=True),
                             Column('samp_id', Integer, ForeignKey('samples.id')),
                             Column('proj_id', Integer, ForeignKey('projects.id'))
)
'''

class Project(Model):
    __tablename__ = 'projects'

    id = Column(Integer, Sequence('projects_id_seq'), primary_key=True)

    name = Column(String(45), nullable=False)
    #sample = Column(ForeignKey(u'samples.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)
    status = Column(ForeignKey(u'proj_status.id'), nullable=False)

    proj_status = relationship(u'ProjectStatus', primaryjoin='Project.status == ProjectStatus.id', backref=u'projects')
    collaborators = relationship('ElaUser', secondary=assoc_users_projects, backref='projects')
    #project_samples = relationship('Sample', secondary=assoc_project_sample, backref='projects')

    def __repr__(self):
      return self.name


class Sample(Model):
    __tablename__ = 'samples'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    nickname = Column(String(45))
    material = Column(ForeignKey(u'materials.id', ondelete=u'RESTRICT', onupdate=u'CASCADE'), nullable=False)

    material_sample = relationship(u'Material', primaryjoin='Sample.material == Material.id')

    def __repr__(self):
      return self.name


class UserType(Model):
    __tablename__ = 'user_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(45), nullable=False)

    def __repr__(self):
      return self.type
