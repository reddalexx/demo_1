from apps.common.schemas import CustomAutoSchema


class CountryChartSchema(CustomAutoSchema):

    query_parameters = [
        {'name': 'q',
         'in': 'query',
         'required': True,
         'description': 'Source',
         'schema': {
             'type': 'string',
             'enum': ['area', 'population']},
         },
    ]
