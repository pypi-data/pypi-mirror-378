class Reference:

    def __init__(self, csv):
        split = csv[:-1].split('(')
        if split[0] == 'REFERENCE':
            self.outgoing = True
        elif split[0] == 'INCOMING_REFERENCE':
            self.outgoing = False
        split = split[1].split('/')
        self.multiple = len(split) > 1 and split[1][:1] == 'n'
        split = split[0].split('.')
        if len(split) > 1:
            self.target = split[1]
            self.package = split[0]
        else:
            self.target = split[0]


    def __str__(self):
        s = f'{'Outgoing' if self.outgoing else 'Incoming'} reference to {'multiple objects' if self.multiple else 'single object'} {self.target} {'in package ' + self.package if self.package else ''}'
        return s
