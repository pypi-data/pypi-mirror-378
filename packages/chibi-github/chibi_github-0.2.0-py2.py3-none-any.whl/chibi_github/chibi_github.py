from chibi_api import Chibi_api
from chibi_api.chibi_api import Chibi_inner_api
from chibi_requests.auth import Bearer

from .response import Create, Delete, Get
from chibi_github.config import configuration


class Github_api_inner( Chibi_inner_api ):
    response = {
        'get': Get,
        'post': Create,
        'delete': Delete,
    }


class Github_api( Chibi_api ):
    schema = 'https'
    host = 'api.github.com'
    inner_api_class = Github_api_inner

    def login( self, token=None ):
        if token is None:
            token = Bearer( token=configuration.github.personal_token )
        else:
            token = Bearer( token=token )
        self.API.auth = token

    @property
    def me( self ):
        return self.API.user
