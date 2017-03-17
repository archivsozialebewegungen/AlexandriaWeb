'''
Created on 17.06.2016

@author: michael
'''
from django import template

register = template.Library()

def image_files(document_file_infos):
    
    filtered_list = []
    for file_info in document_file_infos:
        if file_info.filetype in ('gif', 'tif', 'png', 'jpg'):
            filtered_list.append(file_info)
    return filtered_list

register.filter("image_files", image_files)