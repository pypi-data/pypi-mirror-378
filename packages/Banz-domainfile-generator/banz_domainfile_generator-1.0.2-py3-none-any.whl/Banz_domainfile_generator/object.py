from .field import Field

class Object:

    def __init__(self, csv):
        i = csv.find(';')
        self.package = csv[:i]
        csv = csv[i+1:]
        i = csv.find(';')
        self.name = csv[:i]
        self.fields = dict()
        
        fields = csv[i+1:].split(';')
    
        for f in fields:
            field = Field(f)
            self.fields[field.name] = field

    def __str__(self):
        s = f'Object of name {self.name}'
        for v in self.fields.values():
            s += f'\n{v}'
        return s
    