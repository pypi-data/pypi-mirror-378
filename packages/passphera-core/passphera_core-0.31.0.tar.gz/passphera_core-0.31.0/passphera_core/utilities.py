from passphera_core.exceptions import InvalidPropertyNameException


def check_property_name(func):
    def wrapper(self, prop, value):
        if prop not in {"shift", "multiplier", "key", "algorithm", "prefix", "postfix", "character_replacements"}:
            raise InvalidPropertyNameException(prop)
        return func(self, prop, value)
    return wrapper
