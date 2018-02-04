'''
The views for the basic Alexandria web application
'''
from django import forms
from django.http import HttpResponse
from django.template import loader
from django.template.context import RequestContext
from django.views.generic.base import View
from alexandriabase import baseinjectorkeys
from alexandriabase.domain import AlexDate
import datetime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
import json
from alexandriabase.services.document_pdf_generation_service import TextObject
import traceback
import sys
from alexandriabase.base_exceptions import NoSuchEntityException
from django.http.response import Http404
from alexplugins.systematic import SYSTEMATIC_DAO_KEY
from django.shortcuts import render

def serializable_form_data(form_data):
    
    serializable_form_data = {}
    for key in form_data:
        value = form_data[key]
        if isinstance(value, datetime.date):
            serializable_form_data[key] = {'day': value.day, 'month': value.month, 'year': value.year}
        else:
            serializable_form_data[key] = value;
    return serializable_form_data

def django_form_data(serializable_data):
    
    form_data = {}
    for key in serializable_data:
        value = serializable_data[key]
        try:
            value['day']
        except:
            form_data[key] = value
        else:
            form_data[key] = datetime.date(value['year'], value['month'], value['day'])
    return form_data

def create_rows(items, no_of_columns=3):
    
    rows = []
    columns = []
    counter = 0
    for item in items:
        counter += 1
        columns.append(item)
        if counter % no_of_columns == 0:
            rows.append(columns)
            columns = []
    if len(columns) > 0:
        rows.append(columns)
    return rows
        
class StatisticsView(View):

    injector = None

    def __init__(self, injector):
        
        self.injector = injector
        
    def get(self, request):
        '''
        Collects some statistics from the database
        '''
        dao = self.injector.get(baseinjectorkeys.DOCUMENT_DAO_KEY)
        values = {
            'title': "Alexandria Statistiken",
            'docstats': dao.get_statistics(),
        }
        return HttpResponse(render(request, 'alex/statistics.html', values))

class SystematicView(View):

    injector = None

    def __init__(self, injector):
        
        self.injector = injector
        
    def get(self, request):
        '''
        Builds a tree of systematic items
        '''
        dao = self.injector.get(SYSTEMATIC_DAO_KEY)
        tree = dao.get_tree()
        javascripttree = self.build_javascript_tree("", [tree.root_node])
        values = {
            'title': "Systematik",
            'treedata': javascripttree,
        }
        return HttpResponse(render(request, 'alex/systematic.html', values))
    
    def build_javascript_tree(self, js_object, tree_nodes):
        
        js_object += "[\n"
        for node in tree_nodes:
            js_object += "{\n"
            node_text = "%s" % node
            signature = "%s" % node.entity.id
            js_object += 'text: "%s", \n' % node_text.replace('"', '\\"')
            js_object += 'signature: "%s"' % signature
            if len(node.children) > 0:
                js_object += ",\nnodes: "
                js_object = self.build_javascript_tree(js_object, node.children)
            js_object += "}"
            if node != tree_nodes[-1]:
                js_object += ","
            js_object += "\n"
        js_object += "]"
        return js_object
        

class SearchForm(forms.Form):

    searchterm_field1 = forms.CharField(label='1.Suchbegriff:', max_length=40, required=False)
    searchterm_field2 = forms.CharField(label='2.Suchbegriff:', max_length=40, required=False)
    searchterm_field3 = forms.CharField(label='3.Suchbegriff:', max_length=40, required=False)
    CHOICES=[('and', 'Alle Suchbegriffe müssen vorkommen'),
             ('or', 'Mindestens ein Suchbegriff muß vorkommen')]

    combine_mode = forms.ChoiceField(choices=CHOICES,
                                     widget=forms.RadioSelect(),
                                     required=True,
                                     initial='and',
                                     label='')
    case_sensitive_field = forms.BooleanField(label='Groß-/Kleinschreibung beachten', required=False)

    basic_helper = FormHelper()
    basic_helper.form_tag = False
    basic_helper.disable_csrf = True
    basic_helper.label_class = "col-md-3 voffset2"
    basic_helper.field_class = "col-md-9 voffset1"
    basic_helper.layout = Layout(
        'searchterm_field1',
        'searchterm_field2',
        'searchterm_field3',
        'case_sensitive_field',
        'combine_mode'
        )
    
    def __init__(self, *params, **kw):
        super().__init__(*params, **kw)
        self.entity_helper = FormHelper()
        self.entity_helper.form_tag = False
        self.entity_helper.disable_csrf = True
        self.entity_helper.label_class = self.basic_helper.label_class
        self.entity_helper.field_class = self.basic_helper.field_class
        self.is_valid()

    def _get_searchterms(self):
        searchterms = []
        for i in range(1,4):
            try:
                searchterms.append(self.cleaned_data['searchterm_field%d' % i])
            except KeyError:
                pass
        return searchterms
    
    def _get_combine_mode(self):
        return 'or' == self.cleaned_data['combine_mode']
    
    def _get_case_sensitive(self):
        return self.cleaned_data['case_sensitive_field']

    searchterms = property(_get_searchterms)
    combine_searchterms_by_or = property(_get_combine_mode)
    case_sensitive = property(_get_case_sensitive)
    
class DocumentSearchForm(SearchForm):
    
    signature_field = forms.CharField(label='Standort:', max_length=40, required=False)
    filetype_field = forms.ChoiceField(label='Dateityp:', initial='', choices=[('',''),('txt','txt'),('jpg','jpg')], required=False)
    document_type_field = forms.ChoiceField(label='Dokumenttyp:', initial='', choices=[('',''),('kommt noch','kommt noch'),('weiteres','weiteres')], required=False)

    def __init__(self, *params, **kw):
        super().__init__(*params, **kw)
        self.entity_helper.layout = Layout(
            'signature_field',
            'filetype_field',
            'document_type_field'
        )

    def _get_signature(self):
        try:
            return self.cleaned_data['signature_field']
        except KeyError:
            return None

    def _get_filetype(self):
        try:
            return self.cleaned_data['filetype_field']
        except KeyError:
            return None
        
    def _get_document_type(self):
        try:
            return self.cleaned_data['document_type_field']
        except KeyError:
            return None

    signature = property(_get_signature)
    filetype = property(_get_filetype)
    document_type = property(_get_document_type)

class EventSearchForm(SearchForm):
    
    date_field_attrs = {'data-date-language': 'de',
                        'data-provide': 'datepicker',
                        'data-date-format': "dd.mm.yyyy"}
    
    earliest_date_field = forms.DateField(
        widget=forms.DateInput(attrs=date_field_attrs),
        label="Frühestens:", required=False)
    
    latest_date_field = forms.DateField(
        widget=forms.DateInput(attrs=date_field_attrs),
        label="Spätestens:", required=False)

    def __init__(self, *params, **kw):
        super().__init__(*params, **kw)
        self.entity_helper.layout = Layout(
            'earliest_date_field',
            'latest_date_field'
        )

    def _get_earliest_date(self):
        try:
            earliest_date = self.cleaned_data['earliest_date_field']
        except KeyError:
            return None
        if earliest_date == None:
            return None
        return AlexDate(earliest_date.year, earliest_date.month, earliest_date.day)
    
    def _get_latest_date(self):
        try:
            latest_date = self.cleaned_data['latest_date_field']
        except KeyError:
            return None
        if latest_date == None:
            return None
        return AlexDate(latest_date.year, latest_date.month, latest_date.day)
    
    def _get_local_only(self):
        return None
    
    def _get_unverified_only(self):
        return None
    
    earliest_date = property(_get_earliest_date)
    latest_date = property(_get_latest_date)
    local_only = property(_get_local_only)
    unverified_only = property(_get_unverified_only)

class EntityView(View):
    
    injector = None
    form_class = SearchForm # Set in child class
    search_info_key = None
    title = "Suche"
    
    def __init__(self, injector):
        
        self.injector = injector
        self.service = self.injector.get(baseinjectorkeys.EVENT_SERVICE_KEY)
        self.filter_builder = self.injector.get(baseinjectorkeys.EVENT_FILTER_EXPRESSION_BUILDER_KEY)
        self.template = None
        
    def post(self, request):
        '''
        Processes the documents search form
        '''
        if 'new_search' in request.POST:
            values = self.start_new_search(request)
        else:
            search_info = request.session[self.search_info_key]
            if "continue_search_forward" in request.POST:
                search_info['current_page'] += 1
            else:
                assert("continue_search_backward" in request.POST)
                search_info['current_page'] -= 1
            request.session[self.search_info_key] = search_info
            values = self.continue_search_from_session(request)
            
        return HttpResponse(render(request, self.template, values))
    
    def continue_search_from_session(self, request):

        search_info = request.session[self.search_info_key]
        filter_expression = self.filter_builder.create_filter_expression(
                self.form_class(django_form_data(search_info['form_data'])))
        paginated_result = self.service.find(filter_expression, search_info['current_page'], 10)
        # Number of pages might have changed
        search_info['number_of_pages'] = paginated_result.number_of_pages
        return {'form': self.form_class(initial=django_form_data(search_info['form_data'])),
                'entities': paginated_result.entities,
                'number_of_pages': paginated_result.number_of_pages,
                'current_page': search_info['current_page'],
                'title': self.title}
                
    
    def start_new_search(self, request):
        
        form = self.form_class(request.POST)
        form.is_valid()
        filter_expression = self.filter_builder.create_filter_expression(form)
        paginated_result = self.service.find(filter_expression, 1, 10)
        search_info = {}
        search_info['form_data'] = serializable_form_data(form.cleaned_data)
        search_info['current_page'] = 1
        search_info['number_of_pages'] = paginated_result.number_of_pages
        request.session[self.search_info_key] = search_info

        return {'form': form,
                'entities': paginated_result.entities,
                'number_of_pages': paginated_result.number_of_pages,
                'current_page': 1,
                'title': self.title}

    def get(self, request):

        if self.search_info_key in request.session:
            values = self.continue_search_from_session(request)
        else:
            values = {'form': self.form_class(),
                       'title': self.title}
            
        return HttpResponse(render(request, self.template, values))

class DocumentsView(EntityView):

    form_class = DocumentSearchForm
    search_info_key = "document_search_info"
    title = 'Dokumentensuche'
    
    def __init__(self, injector):
        
        self.injector = injector
        self.template = 'alex/documents.html'
        self.service = self.injector.get(baseinjectorkeys.DOCUMENT_SERVICE_KEY)
        self.document_type_service = self.injector.get(baseinjectorkeys.DOCUMENT_TYPE_SERVICE_KEY)
        config = self.injector.get(baseinjectorkeys.CONFIG_KEY)
        # The following crude syntax prevents eclipse from 
        # supposing an error
        getattr(DocumentSearchForm, 'base_fields')['filetype_field'].choices = \
            self.create_filetype_choices(config) # @UndefinedVariable
        getattr(DocumentSearchForm, 'base_fields')['document_type_field'].choices = \
            self.create_document_type_choices() # @UndefinedVariable
        self.filter_builder = self.injector.get(baseinjectorkeys.DOCUMENT_FILTER_EXPRESSION_BUILDER_KEY)

    def create_filetype_choices(self,config):
        choices = [('','')]
        for filetype in config.filetypes:
            choices.append((filetype, filetype))
        return choices
    
    def create_document_type_choices(self):
        choices = [('','')]
        for document_type_id, description in self.document_type_service.get_document_types().items():
            choices.append((document_type_id, description))
        return choices
    
class EventsView(EntityView):

    form_class = EventSearchForm
    search_info_key = "event_search_info"
    title = 'Ereignissuche'
    
    def __init__(self, injector):
        
        self.injector = injector
        self.template = 'alex/events.html'
        self.service = self.injector.get(baseinjectorkeys.EVENT_SERVICE_KEY)
        self.filter_builder = self.injector.get(baseinjectorkeys.EVENT_FILTER_EXPRESSION_BUILDER_KEY)
        
class ShowDocumentView(View):
    
    injector = None
    
    def __init__(self, injector):
        
        self.injector = injector
        self.document_service = injector.get(baseinjectorkeys.DOCUMENT_SERVICE_KEY)
        self.reference_service = injector.get(baseinjectorkeys.REFERENCE_SERVICE_KEY)
    
    def get(self, request):
        
        document_id = request.GET['document_id']
        try:
            document = self.document_service.get_by_id(document_id)
        except NoSuchEntityException:
            raise Http404()
        document_file_infos = self.document_service.get_file_infos_for_document(document)
        document.number_of_files = len(document_file_infos)
        events = self.reference_service.get_events_referenced_by_document(document)
        values = {
            'document': document,
            'events': events,
            'graphic_file_rows': create_rows(document_file_infos, no_of_columns=4)}
            
        return HttpResponse(render(request, 'alex/document.html', values))

    def get_graphic_rows(self, document_file_infos):
        graphic_file_infos = []
        for file_info in document_file_infos:
            if file_info.filetype in ('gif', 'tif', 'jpg', 'png'):
                graphic_file_infos.append(file_info)
        return create_rows(graphic_file_infos, 4)
    
class ShowEventView(View):
    
    injector = None
    
    def __init__(self, injector):
        
        self.injector = injector
        self.event_service = injector.get(baseinjectorkeys.EVENT_SERVICE_KEY)
        self.reference_service = injector.get(baseinjectorkeys.REFERENCE_SERVICE_KEY)
    
    def get(self, request):
        
        event_id = request.GET['event_id']
        event = self.event_service.get_by_id(event_id)
        documents = self.reference_service.get_documents_referenced_by_event(event)
        document_rows = create_rows(documents, no_of_columns=3)
        referenced_events = self.event_service.get_cross_references(event)
        values = {
            'document_rows': document_rows,
            'referenced_events': referenced_events,
            'len': len(document_rows),
            'event': event}
            
        return HttpResponse(render(request, 'alex/event.html', values))

class PdfDownloadView(View):
    
    injector = None
    
    def __init__(self, injector):
        
        self.injector = injector
        self.document_service = injector.get(baseinjectorkeys.DOCUMENT_SERVICE_KEY)
    
    def get(self, request):
        
        document_id = request.GET['document_id']
        document = self.document_service.get_by_id(document_id)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%08d.pdf"' % int(document_id)
        response.write(self.document_service.get_pdf(document))
        return response
        
class FilePreviewView(View):
    
    injector = None
    
    def __init__(self, injector):
        
        self.injector = injector
        self.document_service = injector.get(baseinjectorkeys.DOCUMENT_SERVICE_KEY)
        self.document_file_manager = injector.get(baseinjectorkeys.DOCUMENT_FILE_MANAGER_KEY)
    
    def get(self, request, file_id):
        
        document_file_info = self.document_service.get_file_info_by_id(file_id)
        thumbnail = self.document_service.get_thumbnail(document_file_info)
        response = HttpResponse(content_type="image/png")
        response.write(thumbnail)
        return response
    
class FileView(View):
    
    injector = None
    
    def __init__(self, injector):
        
        self.injector = injector
        self.document_service = injector.get(baseinjectorkeys.DOCUMENT_SERVICE_KEY)
        self.document_file_manager = injector.get(baseinjectorkeys.DOCUMENT_FILE_MANAGER_KEY)
        self.handlers = {'default': self.image_view,
                         'mp4': self.stream_view}
        self.mime_types = {'mp4': 'video/mp4'}
        
    def get(self, request, file_id):

        document_file_info = self.document_service.get_file_info_by_id(file_id)
        try:
            handler = self.handlers[document_file_info.filetype]
        except KeyError:
            handler = self.handlers['default']
            
        return handler(document_file_info)
    
    def image_view(self, document_file_info):

        display_image = self.document_service.get_display_image(document_file_info)
        response = HttpResponse(content_type="image/png")
        response.write(display_image)
        return response

    def stream_view(self, document_file_info):
    
        path = self.document_file_manager.get_file_path(document_file_info)
        file = open(path, "rb")
        response = HttpResponse(content_type=self.mime_types[document_file_info.filetype])
        response.write(file.read())
        return response
    
class DocumentDisplayView(View):
    
    injector = None
    
    def __init__(self, injector):
        
        self.injector = injector
        self.document_service = injector.get(baseinjectorkeys.DOCUMENT_SERVICE_KEY)
        self.document_file_manager = injector.get(baseinjectorkeys.DOCUMENT_FILE_MANAGER_KEY)
        self.handlers = {'txt': self.text_handler,
                         'mp4': self.video_handler,
                         'default': self.image_handler}
        
    def get(self, request, file_id):
        
        document_file_info = self.document_service.get_file_info_by_id(file_id)

        try:
            handler = self.handlers[document_file_info.filetype]
        except KeyError:
            handler = self.handlers['default']
        
        try:
            result = {'success': True, 'html': handler(document_file_info)}
        except Exception as e:
            result = {'success': False}
            
        json_result = json.dumps(result)
        return HttpResponse(json_result, content_type='application/json')

    def image_handler(self, document_file_info):
        
        # Just to throw an error if the file could not be found
        self.document_file_manager.get_file_path(document_file_info)
        
        return '<img id="modalbody" style="max-width: auto;" src="imageview/%s"/>' % document_file_info.id 

    def text_handler(self, document_file_info):

        text = TextObject(self.document_file_manager.get_file_path(document_file_info))
        paragraphs = text.get_paragraphs()        
        html = '<div id="modalbody">'
        for par in paragraphs[0:1]:
            html += '<h2>%s</h2>' % par
        for par in paragraphs[1:2]:
            html += '<h1>%s</h1>' % par
        for par in paragraphs[2:]:
            html += '<p>%s</p>' % par
        html += '</div>'
        return html
    
    def video_handler(self, document_file_info):
        
        # Just to throw an error if the file could not be found
        self.document_file_manager.get_file_path(document_file_info)

        html = '<video id="modalbody" controls autoplay>'
        html += '<source src="imageview/%s" type="video/%s">' % (
                document_file_info.id,
                document_file_info.filetype)
        html += 'Dieser Browser unterstützt keine Videos'
        html += '</video>'
        return html