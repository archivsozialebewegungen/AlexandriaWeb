from django.test.client import Client
from alex_test_utils import TestEnvironment, TestModule, setup_database_schema,\
    drop_database_schema, load_table_data
from injector import Injector, ClassProvider, singleton, Module
from alexandriabase import AlexBaseModule, baseinjectorkeys
from alexandriabase.daos import DaoModule
from alexandriabase.services import ServiceModule
import os
from django.test.testcases import TestCase
from alexandriabase.daos.basiccreatorprovider import BasicCreatorProvider
from alexplugins.systematic.base import SystematicBasePluginModule
from alexandriaweb.settings import INJECTOR
from daotests.test_base import tables
from alexdbview.views import StatisticsView
import re

class TestStatisticsPage(TestCase):
    
    def setUp(self):
        
        dbengine = INJECTOR.get(baseinjectorkeys.DBEngineKey)
        setup_database_schema(dbengine)
        load_table_data(tables, dbengine)

    def tearDown(self):
        
        dbengine = INJECTOR.get(baseinjectorkeys.DBEngineKey)
        drop_database_schema(dbengine)

    def testLoadStatistics(self):
        
        client = Client()
        response = client.get("/alexandria/statistics")
        print(response.content)
        
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
