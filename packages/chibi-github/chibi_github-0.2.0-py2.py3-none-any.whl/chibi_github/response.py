from chibi_requests import Response
from chibi_requests import status_code
from .serializers import Get_base as Get_serializer
from .exception import Error_bad_token


class Get( Response ):
    serializer = Get_serializer
    is_raise_when_no_ok = True

    def raise_when_no_ok( self ):
        if not self.is_raise_when_no_ok or self.ok:
            return
        http_error_msg = ""
        if self.status_code == status_code.HTTP_401_UNAUTHORIZED:
            raise Error_bad_token( response=self, )
        super().raise_when_no_ok()


class Create( Get ):
    @property
    def ok( self ):
        return self.status_code == 201


class Delete( Get ):
    @property
    def ok( self ):
        return self.status_code == 204
