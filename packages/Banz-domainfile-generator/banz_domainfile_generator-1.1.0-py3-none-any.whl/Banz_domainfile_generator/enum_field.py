class EnumField:

    def __init__(self, csv):
        self.name = csv[0]
        self.enums = []
        for c in csv[1:]:
            self.enums.append(c)

    def __str__(self):
        opt = ', '.join(self.enums)
        s = f'Enum {self.name} {('with options ' + opt) if len(opt) > 0 else 'without options'}'
        return s