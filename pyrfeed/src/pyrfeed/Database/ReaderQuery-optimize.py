#!/usr/bin/env python
# -*- coding : iso-8859-1 -*-

from SmartQuery.Handler import QueryHandler

import ReaderQuery as ReaderQuery
q = QueryHandler( queries=ReaderQuery.queries )
q.writeo( 'ReaderQuery' )
