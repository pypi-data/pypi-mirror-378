import os, pickle

class Manager:
    def __init__(self):
        self._route_file_ = "./pyhook_data"
        self._file_content_ = ".core_triggers"
        self._on_init_()
        self.content = self._load_content_()

    def _on_init_(self):
        if not os.path.exists(self._route_file_):
            os.makedirs(self._route_file_)
        full_path = os.path.join(self._route_file_, self._file_content_ + ".pkl")
        if not os.path.isfile(full_path):
            with open(full_path, 'wb') as f:
                pickle.dump({}, f)

    def _load_content_(self):
        full_path = os.path.join(self._route_file_, self._file_content_ + ".pkl")
        with open(full_path, 'rb') as f:
            return pickle.load(f)
        
    def add_trigger(self, name, func):
        if name not in self.content:
            self.content[name] = []
        self.content[name].append(func)
        self._save_content_()

    def delete_trigger(self, name):
        if name in self.content:
            del self.content[name]
            self._save_content_()

    def get_triggers(self, name) -> list:
        return self.content.get(name, [])
    
    def _save_content_(self):
        full_path = os.path.join(self._route_file_, self._file_content_ + ".pkl")
        with open(full_path, 'wb') as f:
            pickle.dump(self.content, f)