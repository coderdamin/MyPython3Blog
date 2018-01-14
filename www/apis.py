# -*- coding:utf-8 -*-
'JSON API definition'
__author__ = 'ZAM';


class APIError(Exception):
    '''
    the base APIError witch contains error(required), data(optional) and message(optional).
    '''
    def __init__(self, error, data = '', message = '')
        super(APIError, self).__init__(message);
        self.error = error;
        self.data = data;
        self.message = message;
    