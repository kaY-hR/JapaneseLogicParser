from functools import wraps

print_mode = False
def print_return(format_func=lambda x, *args, **kwargs: x):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if print_mode:
                print(format_func(result,*args, **kwargs))
            return result
        return wrapper
    return decorator