from django.conf.urls import url  # @UnresolvedImport
from alexdbview.views import StatisticsView, DocumentsView, EventsView,\
    ShowDocumentView, ShowEventView, PdfDownloadView,\
    FilePreviewView, FileView, SystematicView, DocumentDisplayView
from injector import Injector, Module, inject, ClassProvider, singleton,\
    provides
from alexandriabase import AlexBaseModule, baseinjectorkeys
from alexandriabase.daos import DaoModule
from alexandriabase.services import ServiceModule
from alexdbview import webinjectorkeys
import os
import sys
from alexandriabase.daos.basiccreatorprovider import BasicCreatorProvider
import logging
from alexandriaweb.settings import INJECTOR, CONFIG
import socket

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(os.path.join(CONFIG.logdir, "%s.web.log" % socket.gethostname()))
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

urls = [
    url(r'^statistics$', StatisticsView.as_view(injector=INJECTOR)),
    url(r'^documents$', DocumentsView.as_view(injector=INJECTOR)),
    url(r'^events$', EventsView.as_view(injector=INJECTOR)),
    url(r'^systematic$', SystematicView.as_view(injector=INJECTOR)),
    url(r'^showdocument$', ShowDocumentView.as_view(injector=INJECTOR)),
    url(r'^showevent$', ShowEventView.as_view(injector=INJECTOR)),
    url(r'^pdfdownload$', PdfDownloadView.as_view(injector=INJECTOR)),
    url(r'^imagepreview/(?P<file_id>\d+)$', FilePreviewView.as_view(injector=INJECTOR)),
    url(r'^imageview/(?P<file_id>\d+)$', FileView.as_view(injector=INJECTOR)),
    url(r'^documentdisplay/(?P<file_id>\d+)$', DocumentDisplayView.as_view(injector=INJECTOR)),
]
