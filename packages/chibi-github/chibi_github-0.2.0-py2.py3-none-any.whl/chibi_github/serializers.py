from marshmallow import Schema, INCLUDE, fields


class Github_url( fields.Url ):
    """
    serializa una url de github y agrega las credenciales que se encunetran
    en el contexto
    """

    def _serialize( self, value, attr, obj, **kw ):
        super()._serialize( value, attr, obj, **kw )

    def _deserialize( self, value, attr, data, **kw ):
        parent = self.context[ 'url' ]
        value = super()._deserialize( value, attr, data, **kw )
        return parent.build_from_url( value )


class Parse_url( Schema ):
    url = Github_url()


class Parse_status( Schema ):
    status = fields.Integer( required=False )


class Get_base( Parse_url, Parse_status ):

    class Meta:
        unknown = INCLUDE
