from ..object import Object
from .. import domainfile_generator
from pathlib import Path


def generate(objects: list[Object], paths: dict):
    modelPath = paths['domain'] + 'model\\'
    logicPath = paths['logic']
    servicePath = paths['commonService']
    modelPackage = domainfile_generator.getPackage(modelPath)
    logicPackage = domainfile_generator.getPackage(logicPath)
    servicePackage = domainfile_generator.getPackage(servicePath)
    for uniquePackage in set([object.package for object in objects]):
        Path('.' + servicePath + uniquePackage + '\\impl').mkdir(parents=True, exist_ok=True)
    for object in objects:
        generateBaseService(object, servicePath, servicePackage)
        generateBaseServiceImpl(object, servicePath, servicePackage, modelPackage, logicPackage)
        generateService(object, servicePath, servicePackage)
        generateServiceImpl(object, servicePath, servicePackage)

def generateServiceImpl(object, servicePath, servicePackage):
    path = '.' + servicePath + object.package + '\\impl\\' + object.name + 'ServiceImpl.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {servicePackage + object.package}.impl;\n\n')
            file.write('import io.quarkus.arc.Unremovable;\n')
            file.write('import jakarta.enterprise.context.ApplicationScoped;\n')
            file.write(f'import {servicePackage + object.package}.{object.name}Service;\n\n')
            file.write('@Unremovable\n')
            file.write('@ApplicationScoped\n')
            file.write(f'public class {object.name}ServiceImpl extends Base{object.name}ServiceImpl implements {object.name}Service {{\n')
            file.write('}')

def generateService(object, servicePath, servicePackage):
    path = '.' + servicePath + object.package + '\\' + object.name + 'Service.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {servicePackage + object.package};\n\n')
            file.write(f'public interface {object.name}Service extends Base{object.name}Service {{\n')
            file.write('}')

def generateBaseServiceImpl(object, servicePath, servicePackage, modelPackage, logicPackage):
    with open('.' + servicePath + object.package + '\\impl\\Base' + object.name + 'ServiceImpl.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {servicePackage + object.package}.impl;\n\n')
        file.write('import jakarta.inject.Inject;\n')
        file.write('import jakarta.transaction.Transactional;\n')
        file.write('import jakarta.validation.ConstraintViolation;\n')
        file.write('import jakarta.validation.ValidationException;\n')
        file.write(f'import {servicePackage + object.package}.Base{object.name}Service;\n')
        file.write(f'import {servicePackage + object.package}.dto.{object.name}Dto;\n')
        file.write(f'import {servicePackage + object.package}.util.{object.name}DtoMapper;\n')
        file.write(f'import {modelPackage + object.package}.transfer.{object.name}Bto;\n')
        file.write(f'import {logicPackage + object.package}.{object.name}Logic;\n\n')
        file.write('import java.util.List;\n')
        file.write('import java.util.Set;\n')
        file.write('import java.util.stream.Collectors;\n\n')
        file.write(f'public class Base{object.name}ServiceImpl implements Base{object.name}Service {{\n\n')
        file.write('  @Inject\n')
        file.write(f'  {object.name}Logic logic;\n')
        file.write('  @Inject\n')
        file.write(f'  {object.name}DtoMapper mapper;\n\n')
        file.write('  @Override\n')
        file.write(f'  public void validate({object.name}Dto dto) throws ValidationException {{\n')
        file.write(f'    {object.name}Bto bto = mapper.toBto(dto);\n')
        file.write(f'    Set<ConstraintViolation<{object.name}Bto>> validationResult = logic.validate(bto);\n')
        file.write('    if (!validationResult.isEmpty()) {\n')
        file.write('      String message = validationResult.stream()\n')
        file.write('                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage())).collect(Collectors.joining("\\n"));\n')
        file.write('      throw new ValidationException(message);\n')
        file.write('    }\n')
        file.write('  }\n\n')
        file.write('  @Override\n')
        file.write('  @Transactional\n')
        file.write(f'  public String save({object.name}Dto dto) throws ValidationException {{\n')
        file.write(f'    {object.name}Bto bto = mapper.toBto(dto);\n')
        file.write('    logic.save(bto);\n')
        file.write('    dto.setId(bto.getId());\n')
        file.write('    return dto.getId();\n')
        file.write('  }\n\n')
        file.write('  @Override\n')
        file.write(f'  public {object.name}Dto get(String id) {{\n')
        file.write(f'    {object.name}Bto bto = logic.get(id);\n')
        file.write('    return mapper.toDto(bto);\n')
        file.write('  }\n\n')
        file.write('  @Override\n')
        file.write(f'  public List<{object.name}Dto> getList(List<String> ids) {{\n')
        file.write('    return logic.getList(ids).stream().map(mapper::toDto).toList();\n')
        file.write('  }\n\n')
        file.write('  @Override\n')
        file.write(f'  public List<{object.name}Dto> getAll() {{\n')
        file.write('    return logic.getAll().stream().map(mapper::toDto).toList();\n')
        file.write('  }\n\n')
        file.write('  @Override\n')
        file.write('  @Transactional\n')
        file.write('  public boolean delete(String id) {\n')
        file.write('    return logic.delete(id);\n')
        file.write('  }\n')
        file.write('}')

def generateBaseService(object, servicePath, servicePackage):
    with open('.' + servicePath + object.package + '\\Base' + object.name + 'Service.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {servicePackage + object.package};\n\n')
        file.write('import jakarta.validation.ValidationException;\n')
        file.write(f'import {servicePackage + object.package}.dto.{object.name}Dto;\n\n')
        file.write('import java.util.List;\n\n')
        file.write(f'public interface Base{object.name}Service {{\n\n')
        file.write(f'  void validate({object.name}Dto dto) throws ValidationException;\n\n')
        file.write(f'  String save({object.name}Dto dto) throws ValidationException;\n\n')
        file.write(f'  {object.name}Dto get(String id);\n\n')
        file.write(f'  List<{object.name}Dto> getList(List<String> ids);\n\n')
        file.write(f'  List<{object.name}Dto> getAll();\n\n')
        file.write(f'  boolean delete(String id);\n')
        file.write('}')