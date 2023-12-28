# -*- coding=utf-8
import warnings


def deprecated(message=None, category=DeprecationWarning, stacklevel=2):
    def decorator(obj):
        if isinstance(obj, type):
            class DeprecatedClass(obj):
                def __init__(self, *args, **kwargs):
                    if message:
                        warnings.warn(f"{obj.__name__} is deprecated: {message}", category=category, stacklevel=stacklevel)
                    else:
                        warnings.warn(f"{obj.__name__} is deprecated", category=category, stacklevel=stacklevel)
                    super().__init__(*args, **kwargs)

            return DeprecatedClass
        elif callable(obj):
            def deprecated_func(*args, **kwargs):
                if message:
                    warnings.warn(f"{obj.__name__} is deprecated: {message}", category=category, stacklevel=stacklevel)
                else:
                    warnings.warn(f"{obj.__name__} is deprecated", category=category, stacklevel=stacklevel)
                return obj(*args, **kwargs)

            return deprecated_func
        else:
            raise TypeError("Unsupported object type for @deprecated decorator")

    return decorator
