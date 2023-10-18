import warnings
from .c3l_requester import c3l_request as c3l_req

class Res:
    def __init__(self, api_base, token):
        self.__base_url__ = api_base
        self.__token__ = token
    
        self.check_api_base()
        self.__c3l_req__ = c3l_req(api_base, token)
        
    def check_api_base(self):
        if "api/v1" in self.__base_url__:
            raise ValueError(
                "`base_url` should not specify an API version. Remove trailing /api/v1/"
            )
        if "http://" in self.__base_url__:
            warnings.warn(
                "Canvas may respond unexpectedly when making requests to HTTP "
                "URLs. If possible, please use HTTPS.",
                UserWarning,
            )
        if not self.__base_url__.strip():
            warnings.warn(
                "Canvas needs a valid URL, please provide a non-blank `base_url`.",
                UserWarning,
            )
        if "://" not in self.__base_url__:
            warnings.warn(
                "An invalid `base_url` for the Canvas API Instance was used. "
                "Please provide a valid HTTP or HTTPS URL if possible.",
                UserWarning,
        )
    
    def request(self, method, api, params = {}):
        resp_text = self.__c3l_req__.request(method, api, params)
        return resp_text
