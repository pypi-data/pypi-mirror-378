from ..object import Object
from ..enum_field import EnumField
from ..reference import Reference
from .. import domainfile_generator
from pathlib import Path


def generate(objects: list[Object], paths: dict):
    basePath = paths['domain'] + 'base\\'
    enumPath = paths['domain'] + 'enums\\'
    modelPath = paths['domain'] + 'model\\'
    commonServicePath = paths['commonService']
    basePackage = domainfile_generator.getPackage(basePath)
    modelPackage = domainfile_generator.getPackage(modelPath)
    enumPackage = domainfile_generator.getPackage(enumPath)
    commonServicePackage = domainfile_generator.getPackage(commonServicePath)
    for uniquePackage in set([object.package for object in objects]):
        Path('.' + commonServicePath + uniquePackage + '\\dto').mkdir(parents=True, exist_ok=True)
        Path('.' + commonServicePath + uniquePackage + '\\util').mkdir(parents=True, exist_ok=True)
    for object in objects:
        generateCoreDto(object, commonServicePath, commonServicePackage, basePackage, enumPackage)
        generateDto(object, commonServicePath, commonServicePackage)
        generateCoreDtoMapper(object, commonServicePath, commonServicePackage, basePackage, modelPackage, enumPackage)
        generateDtoMapper(object, commonServicePath, commonServicePackage, basePackage, modelPackage, enumPackage)

def generateDtoMapper(object, commonServicePath, commonServicePackage, basePackage, modelPackage, enumPackage):
    path = '.' + commonServicePath + object.package + '\\util\\' + object.name + 'DtoMapper.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {commonServicePackage + object.package}.util;\n\n')
            file.write('import jakarta.enterprise.context.ApplicationScoped;\n\n')
            file.write('@ApplicationScoped\n')
            file.write(f'public class {object.name}DtoMapper extends {object.name}CoreDtoMapper {{\n\n')
            file.write('}')

def generateCoreDtoMapper(object, commonServicePath, commonServicePackage, basePackage, modelPackage, enumPackage):
    nonReferenceFields = [field for field in object.fields.values() if type(field.fieldType) != Reference]
    nToOneReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and not field.fieldType.multiple]
    oneToNReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and field.fieldType.multiple]
    with open('.' + commonServicePath + object.package + '\\util\\' + object.name + 'CoreDtoMapper.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {commonServicePackage + object.package}.util;\n\n')
        if len(nToOneReferences + oneToNReferences):
            file.write('import jakarta.inject.Inject;\n')
        file.write(f'import {commonServicePackage + object.package}.dto.{object.name}Dto;\n')
        file.write(f'import {basePackage}util.BaseDtoMapper;\n')
        file.write(f'import {modelPackage}{object.package}.transfer.{object.name}Bto;\n')
        file.write('\n')
        if len(oneToNReferences):
            file.write('import java.util.List;\n\n')
        file.write(f'public class {object.name}CoreDtoMapper extends BaseDtoMapper {{\n\n')
        for field in sorted(oneToNReferences + nToOneReferences, key=lambda x: x.name):
            file.write('  @Inject\n')
            file.write(f'  {field.fieldType.target}DtoMapper {field.fieldType.target.lower()}DtoMapper;\n')
        file.write('\n')
        file.write(f'  private void mapPropertiesToBto({object.name}Dto dto, {object.name}Bto bto) {{\n')
        file.write('    mapBaseDtoToBto(dto, bto);\n\n')
        for field in nonReferenceFields:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'    bto.set{fieldName}(dto.get{fieldName}());\n')
        file.write('  }\n\n')
        file.write(f'  private void mapPropertiesToDto({object.name}Bto bto, {object.name}Dto dto) {{\n')
        file.write('    mapBaseBtoToDto(bto, dto);\n\n')
        for field in nonReferenceFields:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'    dto.set{fieldName}(bto.get{fieldName}());\n')
        file.write('  }\n\n')
        file.write(f'  public void mapToBto({object.name}Dto dto, {object.name}Bto bto) {{\n')
        file.write('    if (dto != null) {\n')
        file.write('      mapPropertiesToBto(dto, bto);\n')
        for field in nToOneReferences:
            file.write(f'      if (dto.get{field.fieldType.target}() != null) {{\n')
            file.write(f'        bto.set{field.fieldType.target}({field.fieldType.target.lower()}DtoMapper.toBto(dto.get{field.fieldType.target}()));\n')
            file.write('      }\n')
        for field in oneToNReferences:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'      bto.set{fieldName}(dto.get{fieldName}().stream().map({field.fieldType.target.lower()}DtoMapper::toBto).toList());\n')
        file.write('    }\n')
        file.write('  }\n\n')
        file.write(f'  public {object.name}Bto toBto({object.name}Dto dto) {{\n')
        file.write(f'    {object.name}Bto bto = new {object.name}Bto();\n')
        file.write(f'    mapToBto(dto, bto);\n')
        file.write(f'    return bto;\n')
        file.write('  }\n\n')
        file.write(f'  public void mapToDto({object.name}Bto bto, {object.name}Dto dto) {{\n')
        file.write('    if (bto != null) {\n')
        file.write('      mapPropertiesToDto(bto, dto);\n')
        for field in nToOneReferences:
            file.write(f'      if (bto.get{field.fieldType.target}() != null) {{\n')
            file.write(f'        dto.set{field.fieldType.target}({field.fieldType.target.lower()}DtoMapper.toDto(bto.get{field.fieldType.target}()));\n')
            file.write('      }\n')
        for field in oneToNReferences:
            fieldName = field.name[0].upper() + field.name[1:]
            file.write(f'      dto.set{fieldName}(bto.get{fieldName}().stream().map({field.fieldType.target.lower()}DtoMapper::toDto).toList());\n')
        file.write('    }\n')
        file.write('  }\n\n')
        file.write(f'  public {object.name}Dto toDto({object.name}Bto bto) {{\n')
        file.write(f'    {object.name}Dto dto = new {object.name}Dto();\n')
        file.write(f'    mapToDto(bto, dto);\n')
        file.write(f'    return dto;\n')
        file.write('  }\n')
        file.write('}')
    

def generateDto(object, commonServicePath, commonServicePackage):
    path = '.' + commonServicePath + object.package + '\\dto\\' + object.name + 'Dto.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {commonServicePackage + object.package}.dto;\n\n')
            file.write(f'public class {object.name}Dto extends {object.name}CoreDto {{\n\n')
            file.write('  @Override\n')
            file.write('  public boolean equals(Object object) {\n')
            file.write('    if (object == null) {\n')
            file.write('      return false;\n')
            file.write('    }\n')
            file.write('    if (object.getClass() != this.getClass()) {\n')
            file.write('      return false;\n')
            file.write('    }\n')
            file.write(f'    final {object.name}Dto dto = ({object.name}Dto) object;\n')
            file.write('    if (dto.getId() == null) {\n')
            file.write('      return object == this;\n')
            file.write('    } else {\n')
            file.write('      return this.getId().equals(dto.getId());\n')
            file.write('    }\n')
            file.write('  }\n')
            file.write('}')


def generateCoreDto(object, commonServicePath, commonServicePackage, basePackage, enumPackage):
    nonReferenceFields = [field for field in object.fields.values() if type(field.fieldType) != Reference]
    nToOneReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and not field.fieldType.multiple]
    oneToNReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and field.fieldType.multiple]
    with open('.' + commonServicePath + object.package + '\\dto\\' + object.name + 'CoreDto.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {commonServicePackage + object.package}.dto;\n\n')
        file.write(f'import {basePackage}dto.BaseDto;\n')
        for field in sorted(set([field.fieldType.package + '.dto.' + field.fieldType.target + 'Dto' for field in object.fields.values() if type(field.fieldType) == Reference and hasattr(field.fieldType, 'package') and field.fieldType.package != object.package])):
            file.write('import ' + commonServicePackage + field + ';\n')
        for enum in sorted(set([field.fieldType.name for field in object.fields.values() if type(field.fieldType) == EnumField])):
            file.write(f'import {enumPackage}{enum};\n')
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
        if not linebreak:
            file.write('\n')
        file.write(f'public class {object.name}CoreDto extends BaseDto {{\n\n')
        for field in nonReferenceFields:
            file.write(f'  private {field.fieldType if type(field.fieldType) == str else field.fieldType.name} {field.name};\n')
        if len(nonReferenceFields):
            file.write('\n')
        for field in nToOneReferences:
            file.write(f'  private {field.fieldType.target}Dto {field.name};\n')
        if len(nToOneReferences):
            file.write('\n')
        for field in oneToNReferences:
            file.write(f'  private List<{field.fieldType.target}Dto> {field.name};\n')
        if len(oneToNReferences):
            file.write('\n')        
        writeGetterSetters(file, nonReferenceFields)
        writeGetterSetters(file, nToOneReferences)
        for field in oneToNReferences:
            dataType = f'List<{field.fieldType.target}Dto>'
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
    for field in fields:
        dataType = field.fieldType.name if type(field.fieldType) == EnumField else (field.fieldType if type(field.fieldType) == str else field.fieldType.target + 'Dto')
        fieldName = field.name
        fieldNameUpper = fieldName[0].upper() + fieldName[1:]
        file.write(f'  public {dataType} get{fieldNameUpper}() {{\n')
        file.write(f'    return {fieldName};\n')
        file.write(f'  }}\n\n')
        file.write(f'  public void set{fieldNameUpper}({dataType} {fieldName}) {{\n')
        file.write(f'    this.{fieldName} = {fieldName};\n')
        file.write(f'  }}\n\n')