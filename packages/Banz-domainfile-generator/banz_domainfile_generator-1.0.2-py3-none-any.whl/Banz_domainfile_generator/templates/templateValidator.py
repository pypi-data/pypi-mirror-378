from ..object import Object
from .. import domainfile_generator
from pathlib import Path


def generate(objects: list[Object], paths: dict):
    basePath = paths['domain'] + 'base\\'
    modelPath = paths['domain'] + 'model\\'
    logicPath = paths['logic']
    basePackage = domainfile_generator.getPackage(basePath)
    modelPackage = domainfile_generator.getPackage(modelPath)
    logicPackage = domainfile_generator.getPackage(logicPath)
    for uniquePackage in set([object.package for object in objects]):
        Path('.' + modelPath + uniquePackage + '\\validation\\impl').mkdir(parents=True, exist_ok=True)
    for object in objects:
        generateValidator(object, modelPath, modelPackage)
        generateValidatorImpl(object, modelPath, modelPackage, basePackage)
        generateValidatorRule(object, modelPath, modelPackage)
        generateValidatorRuleImpl(object, logicPath, logicPackage, modelPackage)

def generateValidatorRuleImpl(object, logicPath, logicPackage, modelPackage):
    path = '.' + logicPath + object.package + '\\impl\\' + object.name + 'ValidatorRuleImpl.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {logicPackage + object.package}.impl;\n\n')
            file.write('import jakarta.enterprise.context.ApplicationScoped;\n')
            file.write(f'import {modelPackage + object.package}.validation.{object.name}ValidatorRule;\n\n')
            file.write('@ApplicationScoped\n')
            file.write(f'public class {object.name}ValidatorRuleImpl implements {object.name}ValidatorRule {{\n')
            file.write('}')


def generateValidatorRule(object, modelPath, modelPackage):
    path = '.' + modelPath + object.package + '\\validation\\' + object.name + 'ValidatorRule.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {modelPackage + object.package}.validation;\n\n')
            file.write(f'public interface {object.name}ValidatorRule {{\n')
            file.write('}')


def generateValidatorImpl(object, modelPath, modelPackage, basePackage):
    path = '.' + modelPath + object.package + '\\validation\\impl\\' + object.name + 'ValidatorImpl.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {modelPackage + object.package}.validation.impl;\n\n')
            file.write('import jakarta.inject.Inject;\n')
            file.write('import jakarta.validation.ConstraintValidator;\n')
            file.write('import jakarta.validation.ConstraintValidatorContext;\n')
            file.write(f'import {basePackage}I18N;\n')
            file.write(f'import {modelPackage + object.package}.transfer.{object.name}Bto;\n')
            file.write(f'import {modelPackage + object.package}.validation.{object.name}Validator;\n')
            file.write(f'import {modelPackage + object.package}.validation.{object.name}ValidatorRule;\n\n')
            file.write(f'public class {object.name}ValidatorImpl implements ConstraintValidator<{object.name}Validator, {object.name}Bto> {{\n\n')
            file.write('  @Inject\n')
            file.write('  I18N i18N;\n')
            file.write('  @Inject\n')
            file.write(f'  {object.name}ValidatorRule validatorRule;\n\n')
            file.write('  @Override\n')
            file.write(f'  public void initialize({object.name}Validator constraintAnnotation) {{\n')
            file.write('  }\n\n')
            file.write('  @Override\n')
            file.write(f'  public boolean isValid({object.name}Bto {object.name.lower()}Bto, ConstraintValidatorContext constraintValidatorContext) {{\n')
            file.write('    return true;\n')
            file.write('  }\n')
            file.write('}')


def generateValidator(object, modelPath, modelPackage):
    with open('.' + modelPath + object.package + '\\validation\\' + object.name + 'Validator.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {modelPackage + object.package}.validation;\n\n')
        file.write('import jakarta.validation.Constraint;\n')
        file.write('import jakarta.validation.Payload;\n')
        file.write(f'import {modelPackage + object.package}.validation.impl.{object.name}ValidatorImpl;\n\n')
        file.write(f'import java.lang.annotation.*;\n\n')
        file.write('@Target(ElementType.TYPE)\n')
        file.write('@Retention(RetentionPolicy.RUNTIME)\n')
        file.write(f'@Constraint(validatedBy = {object.name}ValidatorImpl.class)\n')
        file.write('@Documented\n')
        file.write(f'public @interface {object.name}Validator {{\n\n')
        file.write(f'  String message() default \"Error in {object.name}Bto\";\n\n')
        file.write('  Class<?>[] groups() default {};\n\n')
        file.write('  Class<? extends Payload>[] payload() default {};\n')
        file.write('}')