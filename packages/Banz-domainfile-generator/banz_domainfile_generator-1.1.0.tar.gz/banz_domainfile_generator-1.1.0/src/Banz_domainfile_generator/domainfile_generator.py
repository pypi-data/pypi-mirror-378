from .object import Object
from .templates import templateBase, templateBo, templateEnum, templateBto, templateDto, templateValidator, templateLogic, templateService, templateResource, templateLiquibase


def generateTemplates(objects: list, paths: dict):
    templateBase.generate(paths)
    templateBo.generate(objects, paths)
    templateEnum.generate(objects, paths)
    templateBto.generate(objects, paths)
    templateDto.generate(objects, paths)
    templateLogic.generate(objects, paths)
    templateService.generate(objects, paths)
    templateResource.generate(objects, paths)
    templateValidator.generate(objects, paths)
    templateLiquibase.generate(objects, paths)


def run(csv: str, paths: dict):
    objects = []
    for object in csv.split('\n'):
        objects.append(Object(object))
    generateTemplates(objects, paths)


def getPackage(path):
    return path.split('src\\main\\java\\')[1].replace('\\', '.')