from flask_appbuilder import IndexView
#from .views import DeviceModelView, ProjectModelView


class ELAIndexView(IndexView):
    index_template = 'ela_index.html'

#class HomePageView(MultipleView):
#    views = [DeviceModelView, ProjectModelView]
