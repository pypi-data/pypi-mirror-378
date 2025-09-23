from flask import Blueprint, request, url_for, jsonify
from datetime import datetime, timezone, timedelta

class RichBlueprint(Blueprint):
    '''
        Defines a structure for an enriched flask-based blueprint.

        By defaut, it extracts elements from the request header, body, form and query and adds them as object properties with rich structures as lists and dictionaries 

        It defines basic endpoints for RESTFUL behavior which can be easily overriden and extended
    '''

    def __init__(self, name, import_name = __name__, static_folder = None, static_url_path = None, template_folder = None, url_prefix = None, subdomain = None, url_defaults = None, root_path = None, cli_group = None):
        super().__init__(name=name, import_name=import_name, static_folder=static_folder, static_url_path=static_url_path, template_folder=template_folder, url_prefix=url_prefix, subdomain=subdomain, url_defaults=url_defaults, root_path=root_path, cli_group=cli_group)
        self.before_request(self.before_request_callback)
        self.after_request(self.after_request_callback)
        self.filter_list = []
        self.sorting_list = []
        self.request_headers = {}
        self.request_method = ''
        self.request_cookies = {}
        self.request_data={}
        self.request_filters={}
        self.object=None
        self.add_url_rule('/', view_func=self.ep_post, methods=['POST']) 
        self.add_url_rule('', view_func=self.ep_post, methods=['POST']) 
        self.add_url_rule('/', view_func=self.ep_get_many, methods=['GET']) 
        self.add_url_rule('', view_func=self.ep_get_many, methods=['GET']) 
        self.add_url_rule('/<object_id>', view_func=self.ep_get_one, methods=['GET']) 
        self.add_url_rule('/<object_id>', view_func=self.ep_update, methods=['PATCH']) 
        self.add_url_rule('/<object_id>', view_func=self.ep_delete, methods=['DELETE']) 

    def ep_get_one(self, object_id, **kwargs):
        '''
            Assumes object property has been set and that it has a load(id) method

            Uses make_response_from_object method for the return clause
        '''
        self.object.load(object_id)
        try:
            self.object.extend_attributes()
        except AttributeError:
            pass
        return self.make_response_from_object('json')

    def ep_update(self, object_id, **kwargs):
        '''
            Assumes object property has been set and that it has a load(id) method and update(data=dict) method

            Uses make_response_from_object method for the return clause
        '''
        self.object.load(object_id)
        self.object.update(data=self.request_data)
        return self.make_response_from_object('json')

    def ep_delete(self, object_id, **kwargs):
        '''
            Assumes object property has been set and that it has a load(id) method and delete() method

            Uses make_response method for the return clause
        '''
        self.object.load(object_id)
        self.object.delete()
        return self.make_response({'result':'deleted'})

    def ep_get_many(self, **kwargs):
        '''
            Assumes object property has been set and that it has a searcj(list) method

            Uses make_response method for the return clause
        '''
        self.object.search(self.filter_list)
        results = self.object.found
        return self.make_response(results, 'json')

    def ep_post(self, **kwargs): 
        '''
            Assumes object property has been set and that it has a set_from_dict(dict) method and insert() method

            Uses make_response_from_object method for the return clause
        '''
        self.object.user_created = self.api_user_id
        self.object.user_updated = self.api_user_id
        self.object.set_from_dict(self.request_data)
        self.object.insert()
        self.make_response_from_object('json')

    def restart(self): 
        '''
           Empties object and instantiates a new one if it was set
        '''
        try:
            if self.object != None:
                self.object = type(self.object)()
        except AttributeError:
            pass    
        
    def before_request_callback(self):
        '''
           Default behavior is to set support.pre_process_request as callback
        '''
        self.pre_process_request()    
         
    def after_request_callback(self):
        '''
           Default behavior is to set support.post_process_request as callback
        '''
        pass
        
    def build_filter_list(self):       
        '''
           Breaks filters in body - list - or query - string separated by "|" into dim-op-val structures "date >= 2025-04-23" and creates 
           a list of dictionaries with the {dim, op, val} structure in the filter_list property for further processing and easier handling
        '''
        self.filter_list=[]
        self.request_filters = {}
        self.search_limit = self.request_data.get('limit', None)
        filters = []
        valid_ops = ['==', '!=', '<=', '>=', '=~', '<', '>']
        if 'filters' in self.request_data and isinstance(self.request_data.get('filters'), str):
            self.request_filters = request.args.get('filters', '').split('|')
        for f in filters:
            deleted = None

            for op in valid_ops:
                found=False
                try:
                    if op in f:
                        found=True
                        filter_params = f.split(op)
                        dim = filter_params[0]
                        dim_df = [df for df in self.object.data_fields if df.get('name') == dim][0]
                        val = filter_params[1]
                        if dim == 'deleted':
                            deleted = val
                        if dim_df.get('type') == 'bool' or dim_df.get('subtype') == 'bool':
                            val = bool(val)
                        elif dim_df.get('type') == 'number' or dim_df.get('subtype') == 'number':
                            val = float(val)
                        elif dim_df.get('isArray') == True:
                            val = val.split(',')
                            op = 'ANY IN'
                        self.filter_list.append({'dim':dim, 'val':val, 'op':op})
                except:
                    pass
                if found == True:
                    break
        if deleted == None:
            self.filter_list.append({'dim':'deleted', 'val':False, 'op':'=='})


    def build_request_data(self):
        '''
           Extracts form, query and body and puts them in the request_data property
        '''
        self.request_data={}
        self.request_content_type = request.content_type
        if request.content_type == 'application/json' and request.get_json(silent=True) != None:
            self.request_data.update(request.get_json(silent=True))
        elif request.content_type != None and request.content_type.split(";")[0] == 'multipart/form-data':
            self.request_data.update(request.form.to_dict())
        if request.args != None:
            self.request_data.update(request.args.to_dict())
        if 'file' in request.files and request.files['file'].get('filename', '') != '':
            self.request_data['file'] = request.files['file']

    def load_headers(self):
        '''
           Extracts main expected headers: headers, method, cookies, API-User-Id, API-Token, API-Token-Scope,
           User-Id, User-Token, User-Token-Scope, Operation-Id
        '''
        self.request_headers = request.headers
        self.request_method = request.method
        self.request_cookies = request.cookies
        self.api_user_id = self.request_headers.get('API-User-Id')
        self.api_token = self.request_headers.get('API-Token')
        self.api_token_scope = self.request_headers.get('API-Token-Scope')
        self.user_id = self.request_headers.get('User-Id', None)
        self.user_token = self.request_headers.get('User-Token', None)
        self.user_token_scope = self.request_headers.get('User-Token-Scope', None)
        self.operation_id = self.request_headers.get('Operation-Id')
        self.vendor_id=self.request_headers.get('Vendor-ID', None)

    def load_sorting(self):
        '''
           Extracts sort_by from request data and creates a list of dictionaries with {dim, op} structure
           where dim is the dimension and op can be DESC or ASC
        '''
        option_list = self.request_data.get('sort_by', '').split(",")
        sort_list = []
        for o in option_list:
            option_dict = {}
            option = o.split(" ")
            if len(option) > 1:
                option_dict["op"] = option[1]
            option_dict["dim"] = option[0]
            sort_list.append(option_dict)
        sort_list.append({'dim':'_key'})
        self.sorting_list = sort_list


    def pre_process_request(self):
        '''
           Default behavior is to build request_data, filter_list, headers and sorting properties
        '''
        self.build_request_data()
        self.build_filter_list()
        self.load_headers()
        self.load_sorting()

        
    
    def make_response(self, data, format='json'):
        '''
           Builds a restful response from the data provided using the object property and the other endpoints
        '''
        response_data = data if isinstance(data, list) else [data]
        for rd in response_data:
            try:
                resource_uri =url_for('ep_get_one', object_id = self.object.get('_key') )
                rd['resource_uri'] = resource_uri
            except:
                rd['resource_uri'] = ''
        if format == 'json':
            return jsonify({
                "op_date":datetime.now(timezone.utc),
                "op_id":self.operation_id,
                "content": response_data
                })
        if format == 'html':
            ans = ''
            for k in response_data:
                ans = f'{ans}<br><p><b>{k}</b>:{response_data[k]}</p>'
            return ans
        if format == 'native':
            return response_data

    def make_response_from_object(self, format='json'):
        '''
           Builds a restful response using the object property and the other endpoints
        '''
            
        if self.object != None:
            if 'native' in self.scope:
                data =  self.object.to_dict()
            else:
                data = self.object.dict_by_scope(['id', 'basic'])
            return self.make_response(data, format)
        else:
            return jsonify({})
    
    def get_object_get_uri(self):
        '''
           Returns get URI from object property
        '''
        return url_for('ep_get_one', object_id = self.object.get('_key') )


    def make_event(self, user_id, wait_for_response=False):
        '''
           Creates a event for logging, assumes a simple structure were Users, timestamps and enpoints are stored
        '''
        pass
    
