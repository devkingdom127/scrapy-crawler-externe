from http import HTTPStatus


class Error:
    """This is a copy of what was added to sam-admin-back project."""

    @classmethod
    def unauthorized(cls, message="You are not authorized to view this."):
        return cls(code=HTTPStatus.UNAUTHORIZED, message=message)

    @classmethod
    def forbidden(cls, message="You do not have permission to access this ressource."):
        return cls(code=HTTPStatus.FORBIDDEN, message=message)

    @classmethod
    def not_found(cls, message="Record not found"):
        return cls(code=HTTPStatus.NOT_FOUND, message=message)

    @classmethod
    def internal_error(cls, exception, message="Internal error"):
        return cls(code=HTTPStatus.INTERNAL_SERVER_ERROR, message=message + ': ' + str(exception))

    def __init__(self, message: str, code: int):
        self.code = code
        self.message = message

    def response(self):
        return (
            {"code": self.code, "message": self.message},
            self.code
        )
