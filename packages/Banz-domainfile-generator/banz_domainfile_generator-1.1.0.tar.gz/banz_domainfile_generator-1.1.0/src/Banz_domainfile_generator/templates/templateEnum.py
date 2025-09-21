from ..object import Object
from ..enum_field import EnumField
from .. import domainfile_generator
from pathlib import Path


def generate(objects: list[Object], paths: dict):
    enumPath = paths['domain'] + 'enums\\'
    enumPackage = domainfile_generator.getPackage(enumPath)
    Path('.' + enumPath).mkdir(parents=True, exist_ok=True)
    enums = [field.fieldType for object in objects for field in object.fields.values() if type(field.fieldType) == EnumField]
    for enum in enums:
        with open('.' + enumPath + enum.name + '.java', 'w') as file:
            file.write('// generated\n')
            file.write(f'package {enumPackage[:-1]};\n\n')
            file.write(f'public enum {enum.name} {{\n')
            for e in enum.enums:
                file.write(f'  {e},\n')
            file.write('}')
