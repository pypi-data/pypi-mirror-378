from typing import Any, Dict, List, Optional, Callable, Union
from abc import ABC, abstractmethod
import re

from ..types import HookValidator, HookValidationError

class SchemaValidator(HookValidator):
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self._error_message = ""
        
    def validate(self, data: Any) -> bool:
        try:
            return self._validate_value(data, self.schema)
        except Exception as e:
            self._error_message = str(e)
            return False
            
    def get_error_message(self) -> str:
        return self._error_message
        
    def _validate_value(self, value: Any, schema: Dict[str, Any]) -> bool:
        schema_type = schema.get('type')
        
        if schema_type == 'string':
            if not isinstance(value, str):
                self._error_message = f"Expected string, got {type(value).__name__}"
                return False
            return self._validate_string(value, schema)
            
        elif schema_type == 'number' or schema_type == 'integer':
            if schema_type == 'integer' and not isinstance(value, int):
                self._error_message = f"Expected integer, got {type(value).__name__}"
                return False
            elif schema_type == 'number' and not isinstance(value, (int, float)):
                self._error_message = f"Expected number, got {type(value).__name__}"
                return False
            return self._validate_number(value, schema)
            
        elif schema_type == 'boolean':
            if not isinstance(value, bool):
                self._error_message = f"Expected boolean, got {type(value).__name__}"
                return False
            return True
            
        elif schema_type == 'array' or schema_type == 'list':
            if not isinstance(value, (list, tuple)):
                self._error_message = f"Expected array, got {type(value).__name__}"
                return False
            return self._validate_array(value, schema)
            
        elif schema_type == 'object' or schema_type == 'dict':
            if not isinstance(value, dict):
                self._error_message = f"Expected object, got {type(value).__name__}"
                return False
            return self._validate_object(value, schema)
            
        return True
        
    def _validate_string(self, value: str, schema: Dict[str, Any]) -> bool:
        if 'minLength' in schema and len(value) < schema['minLength']:
            self._error_message = f"String too short (min: {schema['minLength']})"
            return False
            
        if 'maxLength' in schema and len(value) > schema['maxLength']:
            self._error_message = f"String too long (max: {schema['maxLength']})"
            return False
            
        if 'pattern' in schema:
            pattern = re.compile(schema['pattern'])
            if not pattern.match(value):
                self._error_message = f"String doesn't match pattern: {schema['pattern']}"
                return False
                
        if 'enum' in schema and value not in schema['enum']:
            self._error_message = f"Value not in allowed values: {schema['enum']}"
            return False
            
        return True
        
    def _validate_number(self, value: Union[int, float], schema: Dict[str, Any]) -> bool:
        if 'minimum' in schema and value < schema['minimum']:
            self._error_message = f"Number too small (min: {schema['minimum']})"
            return False
            
        if 'maximum' in schema and value > schema['maximum']:
            self._error_message = f"Number too large (max: {schema['maximum']})"
            return False
            
        if 'multipleOf' in schema and value % schema['multipleOf'] != 0:
            self._error_message = f"Number not multiple of {schema['multipleOf']}"
            return False
            
        return True
        
    def _validate_array(self, value: Union[List[Any], tuple], schema: Dict[str, Any]) -> bool:
        if 'minItems' in schema and len(value) < schema['minItems']:
            self._error_message = f"Array too short (min items: {schema['minItems']})"
            return False
            
        if 'maxItems' in schema and len(value) > schema['maxItems']:
            self._error_message = f"Array too long (max items: {schema['maxItems']})"
            return False
            
        if 'items' in schema:
            item_schema = schema['items']
            for i, item in enumerate(value):
                if not self._validate_value(item, item_schema):
                    self._error_message = f"Item {i}: {self._error_message}"
                    return False
                    
        return True
        
    def _validate_object(self, value: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        if 'required' in schema:
            for required_key in schema['required']:
                if required_key not in value:
                    self._error_message = f"Missing required property: {required_key}"
                    return False
                    
        if 'properties' in schema:
            for key, prop_schema in schema['properties'].items():
                if key in value:
                    if not self._validate_value(value[key], prop_schema):
                        self._error_message = f"Property '{key}': {self._error_message}"
                        return False
                        
        return True

class TypeValidator(HookValidator):
    def __init__(self, expected_type: type):
        self.expected_type = expected_type
        self._error_message = ""
        
    def validate(self, data: Any) -> bool:
        if not isinstance(data, self.expected_type):
            self._error_message = f"Expected {self.expected_type.__name__}, got {type(data).__name__}"
            return False
        return True
        
    def get_error_message(self) -> str:
        return self._error_message

class RangeValidator(HookValidator):
    def __init__(self, min_val: Optional[Union[int, float]] = None, 
                 max_val: Optional[Union[int, float]] = None):
        self.min_val = min_val
        self.max_val = max_val
        self._error_message = ""
        
    def validate(self, data: Any) -> bool:
        if not isinstance(data, (int, float)):
            self._error_message = f"Expected number, got {type(data).__name__}"
            return False
            
        if self.min_val is not None and data < self.min_val:
            self._error_message = f"Value {data} is below minimum {self.min_val}"
            return False
            
        if self.max_val is not None and data > self.max_val:
            self._error_message = f"Value {data} is above maximum {self.max_val}"
            return False
            
        return True
        
    def get_error_message(self) -> str:
        return self._error_message

class LengthValidator(HookValidator):
    def __init__(self, min_length: Optional[int] = None, max_length: Optional[int] = None):
        self.min_length = min_length
        self.max_length = max_length
        self._error_message = ""
        
    def validate(self, data: Any) -> bool:
        if not hasattr(data, '__len__'):
            self._error_message = f"Object has no length"
            return False
            
        length = len(data)
        
        if self.min_length is not None and length < self.min_length:
            self._error_message = f"Length {length} is below minimum {self.min_length}"
            return False
            
        if self.max_length is not None and length > self.max_length:
            self._error_message = f"Length {length} is above maximum {self.max_length}"
            return False
            
        return True
        
    def get_error_message(self) -> str:
        return self._error_message

class RegexValidator(HookValidator):
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)
        self.pattern_str = pattern
        self._error_message = ""
        
    def validate(self, data: Any) -> bool:
        if not isinstance(data, str):
            self._error_message = f"Expected string, got {type(data).__name__}"
            return False
            
        if not self.pattern.match(data):
            self._error_message = f"String '{data}' doesn't match pattern '{self.pattern_str}'"
            return False
            
        return True
        
    def get_error_message(self) -> str:
        return self._error_message

class ChoiceValidator(HookValidator):
    def __init__(self, choices: List[Any]):
        self.choices = choices
        self._error_message = ""
        
    def validate(self, data: Any) -> bool:
        if data not in self.choices:
            self._error_message = f"Value '{data}' not in allowed choices: {self.choices}"
            return False
        return True
        
    def get_error_message(self) -> str:
        return self._error_message

class CompositeValidator(HookValidator):
    def __init__(self, validators: List[HookValidator], mode: str = "all"):
        self.validators = validators
        self.mode = mode  # "all" or "any"
        self._error_message = ""
        
    def validate(self, data: Any) -> bool:
        if self.mode == "all":
            for validator in self.validators:
                if not validator.validate(data):
                    self._error_message = validator.get_error_message()
                    return False
            return True
        else:  # mode == "any"
            errors = []
            for validator in self.validators:
                if validator.validate(data):
                    return True
                errors.append(validator.get_error_message())
            self._error_message = f"All validations failed: {'; '.join(errors)}"
            return False
            
    def get_error_message(self) -> str:
        return self._error_message

class CallableValidator(HookValidator):
    def __init__(self, validation_func: Callable[[Any], bool], error_message: str = "Validation failed"):
        self.validation_func = validation_func
        self._error_message = error_message
        
    def validate(self, data: Any) -> bool:
        try:
            return self.validation_func(data)
        except Exception as e:
            self._error_message = f"Validation error: {e}"
            return False
            
    def get_error_message(self) -> str:
        return self._error_message

def create_validator(schema_or_type: Union[Dict[str, Any], type, Callable[[Any], bool]]) -> HookValidator:
    if isinstance(schema_or_type, dict):
        return SchemaValidator(schema_or_type)
    elif isinstance(schema_or_type, type):
        return TypeValidator(schema_or_type)
    elif callable(schema_or_type):
        return CallableValidator(schema_or_type)
    else:
        raise ValueError(f"Cannot create validator from {type(schema_or_type)}")

def combine_validators(*validators: HookValidator, mode: str = "all") -> CompositeValidator:
    return CompositeValidator(list(validators), mode)
