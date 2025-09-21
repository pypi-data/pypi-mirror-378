from ..object import Object
from ..enum_field import EnumField
from ..reference import Reference
from pathlib import Path


def generate(objects: list[Object], paths: dict):
    path = paths['schema']
    version = 'v1.0'
    Path('.' + path + version).mkdir(parents=True, exist_ok=True)
    changelogPath = '.' + path + 'changelog.xml'
    with open(changelogPath, 'w') as changelog:
        changelog.write(f'<?xml version="{version}" encoding="UTF-8"?>\n')
        changelog.write('<databaseChangeLog\n')
        changelog.write('        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
        changelog.write('        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"\n')
        changelog.write('        xsi:schemaLocation="\n')
        changelog.write('        http://www.liquibase.org/xml/ns/dbchangelog\n')
        changelog.write('        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.10.xsd">\n\n')
        for object in objects:
            with open('.' + path + version + '\\' + object.name.lower() + '_create.xml', 'w') as file:
                generateLiquibaseFile(file, object)
            changelog.write(f'    <include file="{version}/{object.name.lower()}_create.xml" relativeToChangelogFile="true"/>\n')
        changelog.write('</databaseChangeLog>')


def generateLiquibaseFile(file, object):
    nonReferenceFields = [field for field in object.fields.values() if type(field.fieldType) != Reference]
    nToOneReferences = [field for field in object.fields.values() if type(field.fieldType) == Reference and not field.fieldType.multiple]
    file.write('<databaseChangeLog\n')
    file.write('        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    file.write('        xmlns="http://www.liquibase.org/xml/ns/dbchangelog"\n')
    file.write('        xsi:schemaLocation="\n')
    file.write('        http://www.liquibase.org/xml/ns/dbchangelog\n')
    file.write('        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.10.xsd">\n\n')
    file.write(f'    <changeSet id="{object.name.lower()}-0-0" author="sebanzian">\n')
    file.write('        <preConditions onFail="MARK_RAN">\n')
    file.write('            <not>\n')
    file.write(f'            <tableExists tableName="co_{object.name.lower()}"/>\n')
    file.write('            </not>\n')
    file.write('        </preConditions>\n\n')
    file.write(f'        <createTable tableName="co_{object.name.lower()}">\n')
    file.write('            <column name="id" type="UUID">\n')
    file.write('                <constraints nullable="false" primaryKey="true"/>\n')
    file.write('            </column>\n')
    file.write('            <column name="version" type="INTEGER">\n')
    file.write('                <constraints nullable="false" primaryKey="false"/>\n')
    file.write('            </column>\n')
    file.write('            <column name="creation" type="TIMESTAMP"/>\n')
    file.write('            <column name="creationuser" type="VARCHAR(255)"/>\n')
    file.write('            <column name="lastupdate" type="TIMESTAMP"/>\n')
    file.write('            <column name="lastupdateuser" type="VARCHAR(255)"/>\n\n')
    for field in nonReferenceFields:
        fieldType = "VARCHAR(255)"
        if type(field.fieldType) != EnumField:
            match (field.fieldType):
                case "Integer":
                    fieldType = "int"
                case "BigDecimal":
                    fieldType = "decimal"
                case "Boolean":
                    fieldType = "boolean"
                case "Date":
                    fieldType = "TIMESTAMP"
                case "Timestamp":
                    fieldType = "TIMESTAMP"
        file.write(f'            <column name="{field.name.lower()}" type="{fieldType}"')
        if field.required:
            file.write('>\n')
            file.write('                <constraints nullable="false" primaryKey="false"/>\n')
            file.write('            </column>\n')
        else:
            file.write('/>\n')
    for field in nToOneReferences:
        file.write(f'            <column name="{field.fieldType.target.lower()}_id" type="UUID"')
        if field.required:
            file.write('>\n')
            file.write('                <constraints nullable="false" primaryKey="false"/>\n')
            file.write('            </column>\n')
        else:
            file.write('/>\n')
    file.write('        </createTable>\n')
    for field in nToOneReferences:
        file.write(f'        <addForeignKeyConstraint baseColumnNames="{field.fieldType.target.lower()}_id" baseTableName="co_{object.name.lower()}"\n')
        file.write(f'                                 constraintName="fk_{field.fieldType.target.lower()}" referencedColumnNames="id"\n')
        file.write(f'                                 referencedTableName="co_{field.fieldType.target.lower()}"/>\n')
    file.write('    </changeSet>\n')
    file.write('</databaseChangeLog>')
