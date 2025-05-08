import importlib

def load_class(dotted_path: str):
    if not dotted_path.startswith("app."):
        dotted_path = f"app.{dotted_path}"
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
