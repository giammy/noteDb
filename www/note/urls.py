from django.urls import path, include, re_path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'upload', views.FileUploadViewSet, basename='file')

urlpatterns = [
    #path('', views.index, name='index'),

    # /note
    re_path(r'^note$', views.noteListCreate),

    # /note/int1
    re_path(r'^note/(?P<id>[0-9]+)$', views.noteDetail),

    # /note/?id=int1&rid=int2&lid=int3&type=str1\data=str2
    # re_path(r'^note/?(id=(?P<id>[0-9]+)&)?(rid=(?P<rid>[0-9]+)&)?(lid=(?P<lid>[0-9]+)&)?(type=(?P<type>[0-9A-Za-z]+)&)?(data=(?P<data>[0-9A-Za-z]+))?$', views.noteSearch),
    # re_path(r'^note/include?(iid=(?P<id>[0-9]+)&)?(irid=(?P<rid>[0-9]+)&)?(ilid=(?P<lid>[0-9]+)&)?(itype=(?P<type>[0-9A-Za-z]+)&)?(idata=(?P<data>[0-9A-Za-z]+))?$', views.noteiSearch),
    re_path(r'^note/q?(id=(?P<id>[0-9]+)&)?(rid=(?P<rid>[0-9]+)&)?(lid=(?P<lid>[0-9]+)&)?(type=(?P<type>[0-9A-Za-z]+)&)?(data=(?P<data>[0-9A-Za-z]+))?(iid=(?P<iid>[0-9]+)&)?(irid=(?P<irid>[0-9]+)&)?(ilid=(?P<ilid>[0-9]+)&)?(itype=(?P<itype>[0-9A-Za-z]+)&)?(idata=(?P<idata>[0-9A-Za-z]+))?$', views.noteQuery),

    # /upload/file/
    # i.e: curl -F file=@qrlett/gl_QR.png http://127.0.0.1:8000/note/upload/  
    path('note/', include(router.urls)),

    re_path(r'^note/download/(?P<id>[0-9]+)$', views.noteDownload),
]
