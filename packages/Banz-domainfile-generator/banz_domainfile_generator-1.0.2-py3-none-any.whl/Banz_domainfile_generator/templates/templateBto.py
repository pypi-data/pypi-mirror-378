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
        Path('.' + modelPath + uniquePackage + '\\transfer').mkdir(parents=True, exist_ok=True)
    for object in objects:
        generateCoreBto(object, modelPath, modelPackage, basePackage, enumPackage)
        generateBto(object, modelPath, modelPackage)
        generateCoreBtoMapper(object, modelPath, modelPackage, basePackage)
        generateBtoMapper(object, modelPath, modelPackage)

def generateBtoMapper(object, modelPath, modelPackage):
    path = '.' + modelPath + object.package + '\\transfer\\' + object.name + 'BtoMapper.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {modelPackage + object.package}.transfer;\n\n')
            file.write('import jakarta.enterprise.context.ApplicationScoped;\n\n')
            file.write('@ApplicationScoped\n')
            file.write(f'public class {object.name}BtoMapper extends {object.name}CoreBtoMapper {{\n\n')
            file.write('}')
    

def generateCoreBtoMapper(object, modelPath, modelPackage, basePackage):
    nonReferenceFields = [field for field in object.fields.values() if type(field.fieldType) != Reference]
    nToOneReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and not field.fieldType.multiple]
    oneToNReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and field.fieldType.multiple]
    with open('.' + modelPath + object.package + '\\transfer\\' + object.name + 'CoreBtoMapper.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {modelPackage + object.package}.transfer;\n\n')
        file.write('import jakarta.inject.Inject;\n')
        file.write('import jakarta.persistence.EntityManager;\n')
        file.write(f'import {basePackage}transfer.BaseBtoMapper;\n')
        file.write(f'import {modelPackage}{object.package + '.' + object.name};\n')
        file.write('\n')
        if len(oneToNReferences):
            file.write('import java.util.List;\n')
        file.write('import java.util.Objects;\n\n')
        file.write(f'public class {object.name}CoreBtoMapper extends BaseBtoMapper {{\n\n')
        file.write('  @Inject\n')
        file.write('  EntityManager entityManager;\n')
        for field in sorted(oneToNReferences + nToOneReferences, key=lambda x: x.name):
            file.write('  @Inject\n')
            file.write(f'  {field.fieldType.target}BtoMapper {field.fieldType.target.lower()}BtoMapper;\n')
        file.write('\n')
        file.write(f'  private boolean mapPropertiesToBo({object.name}CoreBto bto, {object.name} bo) {{\n')
        file.write('    boolean result = checkIsNotEqual(bto, bo);\n\n')
        for field in nonReferenceFields:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'    if (!Objects.isNull(bto.get{fieldName}())) {{\n')
            file.write(f'      bo.set{fieldName}(bto.get{fieldName}());\n')
            file.write('    }\n')
        file.write('    return result;\n')
        file.write('  }\n\n')
        file.write(f'  private void mapPropertiesToBto({object.name} bo, {object.name}CoreBto bto) {{\n')
        file.write('    mapBasePropertiesToBto(bo, bto);\n')
        for field in nonReferenceFields:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'    bto.set{fieldName}(bo.get{fieldName}());\n')
        file.write('  }\n\n')
        file.write(f'  public void mapToBto({object.name} bo, {object.name}Bto bto) {{\n')
        file.write(f'    mapPropertiesToBto(bo, bto);\n')
        for field in nToOneReferences:
            file.write(f'    if (bo.get{field.fieldType.target}() != null) {{\n')
            file.write(f'      bto.set{field.fieldType.target}({field.fieldType.target.lower()}BtoMapper.toBto(bo.get{field.fieldType.target}()));\n')
            file.write('    }\n')
        for field in oneToNReferences:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'    bto.set{fieldName}(bo.get{fieldName}().stream().map({field.fieldType.target.lower()}BtoMapper::toBto).toList());\n')
        file.write('  }\n\n')
        file.write(f'  public {object.name}Bto toBto({object.name} bo) {{\n')
        file.write(f'    {object.name}Bto bto = new {object.name}Bto();\n')
        file.write(f'    mapToBto(bo, bto);\n')
        file.write(f'    return bto;\n')
        file.write('  }\n\n')
        file.write(f'  public boolean mapToBo({object.name} bo, {object.name}Bto bto) {{\n')
        for field in nToOneReferences:
            file.write(f'    if (bto.get{field.fieldType.target}() != null) {{\n')
            file.write(f'      bo.set{field.fieldType.target}({field.fieldType.target.lower()}BtoMapper.toBo(bto.get{field.fieldType.target}()));\n')
            file.write('    }\n')
        for field in oneToNReferences:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'    bo.set{fieldName}(bto.get{fieldName}().stream().map({field.fieldType.target.lower()}BtoMapper::toBo).collect(Collectors.toSet()));\n')
        file.write('    return mapPropertiesToBo(bto, bo);\n')
        file.write('  }\n\n')
        file.write(f'  public {object.name} toBo({object.name}Bto bto) {{\n')
        file.write(f'    {object.name} bo;\n')
        file.write(f'    if (bto.getId() != null) {{\n')
        file.write(f'      bo = entityManager.find({object.name}.class, bto.getId());\n')
        file.write('    } else {\n')
        file.write(f'      bo = new {object.name}();\n')
        file.write('    }\n')
        file.write('    mapToBo(bo, bto);\n')
        file.write(f'    return bo;\n')
        file.write('  }\n\n')
        file.write(f'  private boolean checkIsNotEqual({object.name}CoreBto bto, {object.name} bo) {{\n')
        file.write('    return ')
        i = len(nonReferenceFields)
        for field in nonReferenceFields:
            i -= 1
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'!Objects.equals(bo.get{fieldName}(), bto.get{fieldName}())')
            if i  < 1:
                file.write(';\n')
            else:
                file.write('\n             || ')
        file.write('  }\n')
        file.write('}')
        

def generateBto(object, modelPath, modelPackage):
    path = '.' + modelPath + object.package + '\\transfer\\' + object.name + 'Bto.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {modelPackage + object.package}.transfer;\n\n')
            file.write(f'import {modelPackage + object.package}.validation.{object.name}Validator;\n\n')
            file.write(f'@{object.name}Validator\n')
            file.write(f'public class {object.name}Bto extends {object.name}CoreBto {{\n\n')
            file.write('  @Override\n')
            file.write('  public boolean equals(Object object) {\n')
            file.write('    if (object == null) {\n')
            file.write('      return false;\n')
            file.write('    }\n')
            file.write('    if (object.getClass() != this.getClass()) {\n')
            file.write('      return false;\n')
            file.write('    }\n')
            file.write(f'    final {object.name}Bto bto = ({object.name}Bto) object;\n')
            file.write('    if (bto.getId() == null) {\n')
            file.write('      return object == this;\n')
            file.write('    } else {\n')
            file.write('      return this.getId().equals(bto.getId());\n')
            file.write('    }\n')
            file.write('  }\n')
            file.write('}')
            

def generateCoreBto(object, modelPath, modelPackage, basePackage, enumPackage):
    existsRequiredEnum = True in [field.required and type(field.fieldType) == EnumField for field in object.fields.values()]
    existsRequiredNonEnumField = True in [field.required and type(field.fieldType) != EnumField for field in object.fields.values()]
    nonReferenceFields = [field for field in object.fields.values() if type(field.fieldType) != Reference]
    nToOneReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and not field.fieldType.multiple]
    oneToNReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and field.fieldType.multiple]
    with open('.' + modelPath + object.package + '\\transfer\\' + object.name + 'CoreBto.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {modelPackage + object.package}.transfer;\n\n')
        if len(oneToNReferences):
            file.write('import jakarta.validation.Valid;\n')
        if existsRequiredNonEnumField:
            file.write('import jakarta.validation.constraints.NotEmpty;\n')
        if existsRequiredEnum:
            file.write('import jakarta.validation.constraints.NotNull;\n')
        file.write(f'import {basePackage}transfer.BaseBto;\n')
        for enum in sorted(set([field.fieldType.name for field in object.fields.values() if type(field.fieldType) == EnumField])):
            file.write(f'import {enumPackage}{enum};\n')
        for field in sorted(set([field.fieldType.package + '.transfer.' + field.fieldType.target + 'Bto' for field in object.fields.values() if type(field.fieldType) == Reference and hasattr(field.fieldType, 'package') and field.fieldType.package != object.package])):
            file.write('import ' + modelPackage + field + ';\n')
        file.write('\n')
        linebreak = True
        if len([field.fieldType for field in object.fields.values() if field.fieldType == 'BigDecimal']) > 0:
            file.write('import java.math.BigDecimal;\n')
            linebreak = False
        if len([field.fieldType for field in object.fields.values() if field.fieldType == 'Timestamp']) > 0:
            file.write('import java.sql.Timestamp;\n')
            linebreak = False
        if len(oneToNReferences):
            file.write('import java.util.ArrayList;\n')
            linebreak = False
        if len([field.fieldType for field in object.fields.values() if field.fieldType == 'Date']) > 0:
            file.write('import java.util.Date;\n')
            linebreak = False
        if len(oneToNReferences):
            file.write('import java.util.List;\n')
            linebreak = False
        if existsRequiredEnum or existsRequiredNonEnumField:
            file.write('import java.util.Objects;\n')
            linebreak = False
        if not linebreak:
            file.write('\n')
        file.write(f'public class {object.name}CoreBto extends BaseBto {{\n\n')
        for field in nonReferenceFields:
            if field.required and type(field.fieldType) == EnumField:
                file.write('  @NotNull\n')
            elif field.required:
                file.write('  @NotEmpty\n')
            file.write(f'  private {field.fieldType if type(field.fieldType) == str else field.fieldType.name} {field.name};\n\n')
        for field in nToOneReferences:
            if field.required:
                file.write('  @NotEmpty\n')
            file.write(f'  private {field.fieldType.target}Bto {field.name};\n\n')
        for field in oneToNReferences:
            file.write('  @Valid\n')
            file.write(f'  private List<{field.fieldType.target}Bto> {field.name};\n\n')
        writeGetterSetters(file, nonReferenceFields)
        writeGetterSetters(file, nToOneReferences)
        for field in oneToNReferences:
            dataType = f'List<{field.fieldType.target}Bto>'
            fieldName = field.name
            fieldNameUpper = fieldName[0].upper() + fieldName[1:]
            file.write(f'  public {dataType} get{fieldNameUpper}() {{\n')
            file.write(f'    if ({fieldName} == null) {{\n')
            file.write(f'      set{fieldNameUpper}(new ArrayList<>());\n')
            file.write('    }\n')
            file.write(f'    return {fieldName};\n')
            file.write(f'  }}\n\n')
            file.write(f'  public void set{fieldNameUpper}({dataType} {fieldName}) {{\n')
            file.write(f'    this.{fieldName} = {fieldName};\n')
            file.write(f'  }}\n\n')
        file.write('}')
                

def writeGetterSetters(file, fields):
    if len(fields) > 0:
        file.write('\n')
    for field in fields:
        dataType = field.fieldType.name if type(field.fieldType) == EnumField else (field.fieldType if type(field.fieldType) == str else field.fieldType.target + 'Bto')
        fieldName = field.name
        fieldNameUpper = fieldName[0].upper() + fieldName[1:]
        file.write(f'  public {dataType} get{fieldNameUpper}() {{\n')
        file.write(f'    return {fieldName};\n')
        file.write(f'  }}\n\n')
        file.write(f'  public void set{fieldNameUpper}({dataType} {fieldName}) {{\n')
        if (field.required):
            file.write(f'    Objects.requireNonNull({fieldName}, \"{fieldNameUpper} cannot be null.\");\n')
        file.write(f'    this.{fieldName} = {fieldName};\n')
        file.write(f'  }}\n\n')