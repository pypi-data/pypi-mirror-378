from ..object import Object
from ..enum_field import EnumField
from ..reference import Reference
from .. import domainfile_generator
from pathlib import Path


def generate(objects: list[Object], paths: dict):
    modelPath = paths['domain'] + 'model\\'
    basePath = paths['domain'] + 'base\\'
    enumPath = paths['domain'] + 'enums\\'
    modelPackage = domainfile_generator.getPackage(modelPath)
    basePackage = domainfile_generator.getPackage(basePath)
    enumPackage = domainfile_generator.getPackage(enumPath)
    for uniquePackage in set([object.package for object in objects]):
        Path('.' + modelPath + uniquePackage).mkdir(parents=True, exist_ok=True)
    for object in objects:
        with open('.' + modelPath + object.package + '\\' + object.name + '.java', 'w') as file:
            writeImports(file, modelPackage, basePackage, enumPackage, object)
            writeClass(file, modelPackage, object)
            fields = []
            references = []
            for k, v in object.fields.items():
                if type(v.fieldType) == Reference:
                    references.append((k, v))
                else:
                    fields.append((k, v))
            writeConstants(file, fields, references)
            writeFields(file, fields, references)
            writeGetterSetters(file, object.name, fields, references)

def writeImports(file, modelPackage, basePackage, enumPackage, object):
    file.write('// generated\n')
    file.write('package ' + modelPackage + object.package + ';\n\n')
    file.write('import jakarta.persistence.*;\n')
    file.write('import jakarta.validation.constraints.NotEmpty;\n')
    file.write('import jakarta.validation.constraints.NotNull;\n')
    file.write('import ' + basePackage + 'AbstractBusinessObject' + ';\n')
    for field in sorted(set([field.fieldType.name for field in object.fields.values() if type(field.fieldType) == EnumField])):
        file.write('import ' + enumPackage + field + ';\n')
    for field in sorted(set([field.fieldType.package + '.' + field.fieldType.target for field in object.fields.values() if type(field.fieldType) == Reference and hasattr(field.fieldType, 'package') and field.fieldType.package != object.package])):
        file.write('import ' + modelPackage + field + ';\n')
    fieldTypes = set([type(field.fieldType) if type(field.fieldType) != str else field.fieldType for field in object.fields.values()])
    lineBreak = False
    if "BigDecimal" in fieldTypes:
        if not lineBreak:
            file.write('\n')
            lineBreak = True;
        file.write('import java.math.BigDecimal;\n')
    if "Timestamp" in fieldTypes:
        if not lineBreak:
            file.write('\n')
            lineBreak = True;
        file.write('import java.sql.Timestamp;\n')
    if "Date" in fieldTypes:
        if not lineBreak:
            file.write('\n')
            lineBreak = True;
        file.write('import java.util.Date;\n')
    if True in [type(field.fieldType) == Reference and not field.fieldType.outgoing and field.fieldType.multiple for field in object.fields.values()]:
        if not lineBreak:
            file.write('\n')
        file.write('import java.util.HashSet;\n')
        file.write('import java.util.Set;\n')

def writeClass(file, modelPackage, object):
    file.write(f'\n@Entity(\n  name = \"{modelPackage}{object.package}.{object.name}\"\n)\n')
    file.write(f'@Table(\n  name = \"co_{object.name.lower()}\"\n)\n')
    file.write(f'public class {object.name} extends AbstractBusinessObject {{\n\n')

def writeConstants(file, fields, references):
    for field in fields:
        constant = ''.join(['_'+c if c.isupper() else c.upper() for c in field[0]])
        file.write(f'  public static final String {constant} = \"{field[0]}\";\n')
    file.write('\n')
    for ref in references:
        constant = ''.join(['_'+c if c.isupper() else c.upper() for c in ref[0]])
        file.write(f'  public static final String {constant} = \"{ref[0]}\";\n')
    file.write('\n')

def writeFields(file, fields, references):
    for field in fields:
        isEnum = type(field[1].fieldType) == EnumField
        dataType = field[1].fieldType.name if isEnum else field[1].fieldType
        file.write(f'  @Basic\n')
        if field[1].required:
            file.write(f'  @NotEmpty()\n')
        if (isEnum):
            file.write(f'  @Enumerated(EnumType.STRING)\n')
        file.write(f'  @Access(AccessType.FIELD)\n')
        file.write(f'  private {dataType} {field[0]};\n\n')
    for ref in references:
        if ref[1].fieldType.multiple:
            file.write(f'  @OneToMany(\n')
            file.write(f'    cascade = {{\n')
            file.write(f'      CascadeType.REMOVE\n')
            file.write(f'    }},\n')
            file.write(f'    fetch = FetchType.LAZY,\n')
            file.write(f'    orphanRemoval = true\n')
            file.write(f'  )\n')
            file.write(f'  private Set<{ref[1].fieldType.target}> {ref[0]};\n\n')
        else:
            file.write(f'  @ManyToOne(fetch = FetchType.LAZY)\n')
            if ref[1].required:
                file.write(f'  @NotEmpty()\n')
            file.write(f'  private {ref[1].fieldType.target} {ref[0]};\n\n')
    file.write('\n')

def writeGetterSetters(file, objectName, fields, references):
    for field in fields:
        dataType = field[1].fieldType.name if type(field[1].fieldType) == EnumField else field[1].fieldType
        name = field[0][0].upper() + field[0][1:]
        file.write(f'  public {dataType} get{name}() {{\n')
        file.write(f'    return {field[0]};\n')
        file.write(f'  }}\n\n')
        file.write(f'  public void set{name}(final {dataType} {field[0]}) {{\n')
        file.write(f'    this.{field[0]} = {field[0]};\n')
        file.write(f'  }}\n\n')
    file.write('\n')
    for ref in references:
        dataType = ref[1].fieldType.target
        name = ref[0][0].upper() + ref[0][1:]
        if ref[1].fieldType.multiple:
            dataType = f'Set<{dataType}>'
        file.write(f'  public {dataType} get{name}() {{\n')
        file.write(f'    return {ref[0]};\n')
        file.write(f'  }}\n\n')
        file.write(f'  public void set{name}(final {dataType} {ref[0]}) {{\n')
        file.write(f'    this.{ref[0]} = {ref[0]};\n')
        file.write(f'  }}\n\n')
        if ref[1].fieldType.multiple:
            fieldName = ref[0][:-1]
            dataType = ref[1].fieldType.target
            file.write(f'  public boolean add{dataType}(final {dataType} {fieldName}) {{\n')
            file.write(f'    if ({fieldName} == null) {{\n')
            file.write(f'      return false;\n')
            file.write(f'    }}\n')
            file.write(f'    {fieldName}.set{objectName[0].upper() + objectName[1:]}(this);\n')
            file.write(f'    if (!(this.{ref[0]}.contains({fieldName}))) {{\n')
            file.write(f'      return this.{ref[0]}.add({fieldName});\n')
            file.write(f'    }}\n')
            file.write(f'    return false;\n')
            file.write(f'  }}\n')
    file.write('}')