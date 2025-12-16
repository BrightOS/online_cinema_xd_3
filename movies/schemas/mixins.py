from typing import Any, Dict
from pydantic import Field


class ExampleMixin:
    @classmethod
    def model_json_schema(cls, **kwargs) -> Dict[str, Any]:
        schema = super().model_json_schema(**kwargs)
        example = {}

        for field_name, field_info in cls.model_fields.items():
            if field_info.json_schema_extra and isinstance(field_info.json_schema_extra, dict):
                if 'example' in field_info.json_schema_extra:
                    example[field_name] = field_info.json_schema_extra['example']
            elif field_info.examples:
                example[field_name] = field_info.examples[0]

        if example:
            schema['examples'] = [example]

        return schema
