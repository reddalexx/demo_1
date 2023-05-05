import re

from rest_framework.schemas.openapi import AutoSchema


class CustomAutoSchema(AutoSchema):
    query_parameters = []

    def get_operation_id(self, path, method):
        """
        Compute an operation ID from path and method name to be unique.
        """
        path_name = '-'.join([i for i in path.strip('/').split('/')])
        path_name = re.sub(r'[{}]', '', path_name)
        return f'{path_name}-{method}'

    def get_operation(self, path, method):
        """
        Extend operation with query params
        """
        op = super().get_operation(path, method)
        op['parameters'] += self.get_query_parameters(path, method)
        return op

    def get_query_parameters(self, path, method):
        return self.query_parameters
