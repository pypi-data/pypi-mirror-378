
class DictOfLists(dict):
    """
    All valeus are List
    If a non existing key is called, an empty list will be created as the value
    """
    
    def __setitem__(self, key, value):
        value_type = type(value).__name__
        if value_type != 'list':
            value = [value]
            
        dict.__setitem__(self, key, value)
    
    
    def __getitem__(self, key):
        if key not in list(self.keys()):
            self[key] = []
        return super().__getitem__(key)


class DictOfSets(dict):
    """
    All values are sets
    If a non existing key is called, an empty set will be created as the value
    """
    
    def __setitem__(self, key, value):
        value_type = type(value).__name__
        if value_type != 'set':
            value = {value}
            
        dict.__setitem__(self, key, value)
    
    
    def __getitem__(self, key):
        if key not in list(self.keys()):
            self[key] = set({})
        return super().__getitem__(key)
