import dill
from src.CiF.BCiF import BCiF


def save_model(model: BCiF, path: str) -> None:
    with open(path, 'wb') as f:
        dill.dump(model, f)


def load_model(path: str) -> BCiF:
    with open(path, 'rb') as f:
        obj = dill.load(f)
    if not isinstance(obj, BCiF):
        raise ValueError('Loaded object is not a BCiF model')
    return obj
