class Error_bad_token( Exception ):
    def __init__( self, response ):
        self.response = response

    def __str__( self ):
        return (
            "el token es incorrecto o esta expirado "
            "https://github.com/settings/personal-access-tokens"
        )
