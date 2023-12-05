import requests as req
import json

class BearerAuth(req.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class c3l_request:
    def __init__(self, base, token = None):
        self.__base__ = base
        self.__auth__ = None
        if None != token:
            self.__auth__ = BearerAuth(token)
  
    def __get_url__(self, api):
      return f"{self.__base__}/{api}" if None != self.__base__ else api
    
    def __process_api__(self, method, api, params):
        if 'get' == method.strip().lower():
            page = 1
            per_page = 100
            if params.__contains__('page'):
                page = params['page']
            if params.__contains__('perpage'):
                page = params['page']
            api = f'{api}?page={page}&per_page={per_page}'
        return api
    
    def __get_link_info__(self, line):
        parts = line.split(';')
        parts_n = parts[0].split('&')
        page = parts_n[0][parts_n[0].index('=') + 1]
        per_page = parts_n[1][parts_n[1].index('=') + 1:-1]
        rel = parts[1][parts[1].index('=') + 2: -1]
        return (page, per_page, rel)

    def __process_resp__(self, method, resp):
        rc = resp.text
        if 'get' != method.strip().lower():
            return rc
        if 200 == resp.status_code:
            link_header = resp.headers.get('Link')
            if None is not link_header:
                link_header.split(',')
                rc = { 'result': json.loads(resp.text) }
                ret = map(self.__get_link_info__, link_header.split(','))
                for i in ret:
                    rc[i[2]] = i[0]
                    rc['per_page'] = i[1]
                rc = json.dumps(rc)
        return rc

    def request(self, method, api, params = {}):
        request_method = None
        if 'post' == method.strip().lower():
            request_method = req.post
        elif 'get' == method.strip().lower():
            api = self.__process_api__(method, api, params)
            request_method = req.get
        elif 'put' == method.strip().lower():
            request_method = req.put
        elif 'delete' == method.strip().lower():
            request_method = req.delete
        else:
            raise 'method invalid'
        resp = request_method(self.__get_url__(api), params=params, auth=self.__auth__)
        return self.__process_resp__(method, resp)

