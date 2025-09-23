from flask import jsonify

def f_page_not_found():
    '''
        Managed error for Page not Found
    '''
    return jsonify('This page does not exist'), 404
