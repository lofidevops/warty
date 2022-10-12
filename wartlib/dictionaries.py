def flat_dictionary(nested: dict):
    flat = {}
    for key, value in nested.items():
        for k, v in flat_pair(key, value):
            flat[k] = v
    return flat


def flat_pair(key, value):
    if type(value) == dict:
        for k, v in value.items():
            for p, q in flat_pair(f"{key}.{k}", v):
                yield p, q
    elif type(value) == list:
        yield f"{key}", value
        for i, item in enumerate(value):
            for p, q in flat_pair(f"{key}._{i}", item):
                yield p, q
    else:
        yield str(key), value
