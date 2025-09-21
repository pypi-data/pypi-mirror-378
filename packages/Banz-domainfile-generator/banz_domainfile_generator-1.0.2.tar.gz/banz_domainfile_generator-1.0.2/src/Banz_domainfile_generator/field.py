from .enum_field import EnumField
from .reference import Reference

class Field:

    def __init__(self, field):
        args = field.split(',')
        self.name = args[0]
        fieldType = args[1]
        self.required = len(args) > 2 and args[2] == 'required'
        if fieldType[:4] == 'ENUM':
            enum = fieldType[5:-1].split('/')
            self.fieldType = EnumField(enum)
        elif fieldType[:9] == 'REFERENCE' or fieldType[:18] == 'INCOMING_REFERENCE':
            self.fieldType = Reference(fieldType)
        else:
            self.fieldType = Field.getJavaTypeFromEnum(fieldType)

    def __str__(self):
        s = f'{'Required f' if self.required else 'F'}ield {self.name} of type {self.fieldType}'
        return s

    def getJavaTypeFromEnum(enum):
        match enum:
            case "INTEGER":
                return "Integer"
            case "STRING":
                return "String"
            case "DECIMAL":
                return "BigDecimal"
            case "BOOLEAN":
                return "Boolean"
            case "DATE":
                return "Date"
            case "TIMESTAMP":
                return "Timestamp"