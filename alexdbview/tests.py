from django.test.client import Client
from alex_test_utils import setup_database_schema,\
    drop_database_schema, load_table_data
from alexandriabase import baseinjectorkeys
from django.test.testcases import TestCase
from alexandriaweb.settings import INJECTOR
from daotests.test_base import tables
from alexdbview.views import StatisticsView, DocumentsView
import re

class TestAlexandriaWebPage(TestCase):
    
    def setUp(self):
        
        dbengine = INJECTOR.get(baseinjectorkeys.DB_ENGINE_KEY)
        setup_database_schema(dbengine)
        load_table_data(tables, dbengine)
        self.client = Client()

    def tearDown(self):
        
        dbengine = INJECTOR.get(baseinjectorkeys.DB_ENGINE_KEY)
        drop_database_schema(dbengine)

    def testLoadStatistics(self):
        
        response = self.client.get("/alexandria/statistics")
        
        # Request was successful
        self.assertEqual(response.status_code, 200)
        # The rendered view was the statistics view
        self.assertEqual(response.resolver_match.func.__name__,
                         StatisticsView.as_view().__name__)
        
        # Test that the statistics information is correct
        content = response.content.decode("utf-8")
        pairs = (("Dokumente", "7"),
                 ("Dokumentdateien", "14"),
                 ("tif-Dateien", "4"),
                 ("gif-Dateien", "1"),
                 ("pdf-Dateien", "1"),
                 ("mpg-Dateien", "1"),
                 ("txt-Dateien", "3"),
                 ("jpg-Dateien", "4")
                 )
        for pair in pairs:
            matcher = re.search('%s:</td>\s*?<td>(\d+)</td>' % pair[0],
                                content)        
            self.assertEqual(pair[1], matcher.group(1))

    def _get_document_post_parameters(self):
        
        return {'searchterm_field1': '',
                'searchterm_field2': '',
                'searchterm_field3': '',
                'combine_mode': 'and',
                'location_field': '',
                'filetype_field': '',
                'document_type_field': '',
                'new_search': 'Suche',
                }

    def testGetDocumentsSearchPage(self):

        response = self.client.get("/alexandria/documents")
        
        # Request was successful
        self.assertEqual(response.status_code, 200)
        # The rendered view was the statistics view
        self.assertEqual(response.resolver_match.func.__name__,
                         DocumentsView.as_view().__name__)
        
    def testExecuteDocumentsSearchI(self):
        '''
        Testing a searchterm
        '''
        params = self._get_document_post_parameters()
        params['searchterm_field2'] = 'stes' # document 1 and 6
        response = self.client.post("/alexandria/documents", params)
        
        # Request was successful
        self.assertEqual(response.status_code, 200)
        # The rendered view was the statistics view
        self.assertEqual(response.resolver_match.func.__name__,
                         DocumentsView.as_view().__name__)
        
        content = response.content.decode("utf-8")
        self.assertTrue(re.search('Erstes Dokument', content) is not None)        
        self.assertTrue(re.search('Sechstes Dokument', content) is not None)        
        self.assertTrue(re.search('Siebtes Dokument', content) is None)        

    def testExecuteDocumentsSearchII(self):
        '''
        Testing for document type
        '''
        params = self._get_document_post_parameters()
        params['document_type_field'] = '13' # document 4 and 5
        response = self.client.post("/alexandria/documents", params)
        
        # Request was successful
        self.assertEqual(response.status_code, 200)
        # The rendered view was the statistics view
        self.assertEqual(response.resolver_match.func.__name__,
                         DocumentsView.as_view().__name__)
        
        content = response.content.decode("utf-8")
        self.assertTrue(re.search('Viertes Dokument', content) is not None)        
        self.assertTrue(re.search('Fünftes Dokument', content) is not None)        
        self.assertTrue(re.search('Siebtes Dokument', content) is None)        
