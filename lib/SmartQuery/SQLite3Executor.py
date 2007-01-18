#!/usr/bin/env python

import sqlite3
import Executor

class QueryExecutor( Executor.QueryExecutor ) :
    def __init__(self,dbname,queries) :
        Executor.QueryExecutor.__init__(self,queries,dbname)
        self.__in_transaction = False

    def _get_connection(self,dbname):
        return sqlite3.connect(dbname)
    def _use_seq(self) : return False
    def _use_dict(self) : return False
