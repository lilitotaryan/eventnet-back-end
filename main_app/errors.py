class MainAppException(Exception):
    massage = ""
    code = 1
    default_code = ""
    fields = []

    def __init__(self, code=1, message='', default_code="", fields=[]):
        if message and type(message) is str:
            self.message = message
        if default_code and type(default_code) is str:
            self.default_code = default_code
        if code and type(code) is int:
            self.code = code
        if fields and type(fields) is list:
            self.fields = fields

    def serialize(self):
        return dict(
            error_code=self.code,
            error_message=self.message,
            error_detail=self.default_code,
            fields=self.fields
        )