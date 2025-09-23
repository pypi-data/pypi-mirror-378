import re
from typing import Callable
from enum import Enum, EnumType

def get_dict(data: dict, filter_func: Callable[[str, str, bool], None] | None = None) -> dict[str, any]:
	keys = []
	for key, value in data.items():
		is_function = isinstance(value, Callable)
		if filter_func and not filter_func(key, value, is_function):
			continue
		elif not filter_func and (key.startswith('_') or not is_function):
			continue
		keys.append(key)
	return { key: value for key, value in data.items() if key in keys }


def get_enum_data(enum: EnumType) -> dict[str, any]:
	return { key.name: key.value for key in enum }


def get_enum_str(value: Enum | str) -> str | None:
	return value if type(value) == str else (value.value if value is not None else None)


def add(self: any, list_var: str, data: list):
	if not hasattr(self, list_var):
		raise ValueError(f'Invalid key: {list_var}')
	var: list = getattr(self, list_var)
	if type(var) is not list:
		raise ValueError(f'Variable "{list_var}" is not a list')
	setattr(self, list_var, [*var, *data])
	return self


def add_list(self: any, list_var: str, data: tuple, modifier_func: callable = None):
	for item in data:
		value = modifier_func(item) if modifier_func else item
		add(self, list_var, [value])
	return self


def format(string: str, *args: str, **kwargs: any):
	for arg in args:
		string = re.sub(r'{\d*}', arg, string, count=1)
	for key, arg in kwargs:
		string = re.sub('{' + key + '}', arg, string)
	return string