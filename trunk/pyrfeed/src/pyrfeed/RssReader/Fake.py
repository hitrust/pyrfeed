#!/usr/bin/env python

import os
import sys

from pyrfeed.RssReader.Info import RssReaderInfo

class Reader(object) :
    def __init__(self,config) :
        self._items = [
            {
                'title' : 'Test',
                'content' : repr(sys.argv),
                'link' : '',
                'categories' : ['test','test2'],
                },
            {
                'title' : 'Praf',
                'content' : '<i>'+str(sys.hexversion)+'</i><img src="http://www.google.com/logos/holiday06_1.gif"><iframe src="http://google.com/"></iframe>',
                'link' : 'http://google.com/',
                'categories' : ['google','page','iframe'],
                },
            {
                'title' : '',
                'content' : u'Test \xe9 \u00e9',
                'link' : None,
                'categories' : [],
                },
            {
                'title' : 'Glut',
                'content' : str(os.listdir('.')),
                'link' : '',
                'categories' : [],
                },
            {
                'title' : 'Mank',
                'content' : sys.copyright.replace('e','<b>e</b>'),
                'link' : '',
                'categories' : ['bold'],
                },
            ]
        self._filters = [
            'Test',
            'Choice1',
            'Choice2',
            ]
        self._filter = ''

    def synchro(self) :
        pass

    def reload(self) :
        pass

    def get_titles(self,filter_command=None) :
        return map(lambda x:x['title'],self._items)

    def get_content(self, position) :
        return self._items[position]['content']

    def get_link(self, position) :
        return self._items[position]['link']

    def get_categories(self, position) :
        return self._items[position]['categories']

    def get_filters(self) :
        return self._filters

    def mark_as_read( self, positions ) :
        self._items[0]['content'] = str(positions)

    def mark_as_unread( self, positions ) :
        pass

    def add_star( self, positions ) :
        pass

    def del_star( self, positions ) :
        pass

    def add_public( self, positions ) :
        pass

    def del_public( self, positions ) :
        pass

    def add_label( self, positions, label ) :
        pass

    def del_label( self, positions, label ) :
        pass

    def get_filter(self) :
        return self._filter

    def set_filter(self,filter_command) :
        self._filter = filter_command

class RssReaderInfoFake(RssReaderInfo) :
    names = ['Fake','test']
    priority = 10
    def get_rss_reader(self) :
        return Reader(self._config)
    def get_doc(self) :
        return ""
