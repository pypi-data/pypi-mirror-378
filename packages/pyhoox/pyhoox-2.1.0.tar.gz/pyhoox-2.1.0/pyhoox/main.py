from pyhoox import hooks

def use(name, func):
    if name not in hooks:
        hooks[name] = []
    hooks[name].append(func)
    
def trigger(name, *args, **kwargs):
    if name in hooks:
        for func in hooks[name]:
            func(*args, **kwargs)
