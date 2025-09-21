from ..object import Object
from .. import domainfile_generator
from pathlib import Path


def generate(objects: list[Object], paths: dict):
    logicPath = paths['logic']
    servicePath = paths['commonService']
    resourcePath = paths['uiService']
    logicPackage = domainfile_generator.getPackage(logicPath)
    servicePackage = domainfile_generator.getPackage(servicePath)
    resourcePackage = domainfile_generator.getPackage(resourcePath)
    for uniquePackage in set([object.package for object in objects]):
        Path('.' + resourcePath + uniquePackage + '\\base').mkdir(parents=True, exist_ok=True)
    for object in objects:
        generateBaseResource(object, resourcePath, resourcePackage, servicePackage)
        generateResource(object, resourcePath, resourcePackage, servicePackage)

def generateResource(object, resourcePath, resourcePackage, servicePackage):
    path = '.' + resourcePath + object.package + '\\' + object.name + 'Resource.java'
    if not Path(path).exists():
        with open(path, 'w') as file:
            file.write(f'package {resourcePackage + object.package};\n\n')
            file.write('import jakarta.ws.rs.Consumes;\n')
            file.write('import jakarta.ws.rs.Path;\n')
            file.write('import jakarta.ws.rs.Produces;\n')
            file.write('import jakarta.ws.rs.core.MediaType;\n')
            file.write(f'import {resourcePackage + object.package}.base.Base{object.name}Resource;\n\n')
            file.write(f'@Path("/ui/{object.package}")\n')
            file.write('@Produces({MediaType.APPLICATION_JSON})\n')
            file.write('@Consumes({MediaType.APPLICATION_JSON})\n')
            file.write(f'public class {object.name}Resource extends Base{object.name}Resource {{\n')
            file.write('}')

def generateBaseResource(object, resourcePath, resourcePackage, servicePackage):
    with open('.' + resourcePath + object.package + '\\base\\Base' + object.name + 'Resource.java', 'w') as file:
        file.write('// generated\n')
        file.write(f'package {resourcePackage + object.package}.base;\n\n')
        file.write('import jakarta.inject.Inject;\n')
        file.write('import jakarta.validation.ValidationException;\n')
        file.write('import jakarta.ws.rs.*;\n')
        file.write('import jakarta.ws.rs.core.MediaType;\n')
        file.write(f'import {servicePackage + object.package}.{object.name}Service;\n')
        file.write(f'import {servicePackage + object.package}.dto.{object.name}Dto;\n\n')
        file.write('import java.util.List;\n\n')
        file.write(f'public class Base{object.name}Resource {{\n\n')
        file.write('  @Inject\n')
        file.write(f'  {object.name}Service service;\n\n')
        file.write('  @POST\n')
        file.write('  @Path("validate")\n')
        file.write(f'  public void validate({object.name}Dto dto) throws ValidationException {{\n')
        file.write('    service.validate(dto);\n')
        file.write('  }\n\n')
        file.write('  @POST\n')
        file.write('  @Path("save")\n')
        file.write(f'  public String save({object.name}Dto dto) throws ValidationException {{\n')
        file.write('    return service.save(dto);\n')
        file.write('  }\n\n')
        file.write('  @GET\n')
        file.write('  @Path("get")\n')
        file.write('  @Consumes({MediaType.TEXT_PLAIN})\n')
        file.write(f'  public {object.name}Dto get(@QueryParam("id") String id) {{\n')
        file.write('    return service.get(id);\n')
        file.write('  }\n\n')
        file.write('  @GET\n')
        file.write('  @Path("getList")\n')
        file.write(f'  public List<{object.name}Dto> getList(@QueryParam("ids") List<String> ids) {{\n')
        file.write('    return service.getList(ids);\n')
        file.write('  }\n\n')
        file.write('  @GET\n')
        file.write('  @Path("getAll")\n')
        file.write(f'  public List<{object.name}Dto> getAll() {{\n')
        file.write('    return service.getAll();\n')
        file.write('  }\n\n')
        file.write('  @DELETE\n')
        file.write('  @Path("delete")\n')
        file.write(f'  public boolean delete(@QueryParam("id") String id) {{\n')
        file.write('    return service.delete(id);\n')
        file.write('  }\n')
        file.write('}')