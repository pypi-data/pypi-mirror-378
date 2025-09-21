// generated
package org.derbanz.cluborga.commonservice.organization;

import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.dto.PersonDto;

import java.util.List;

public interface BasePersonService {

  void validate(PersonDto dto) throws ValidationException;

  String save(PersonDto dto) throws ValidationException;

  PersonDto get(String id);

  List<PersonDto> getList(List<String> ids);

  List<PersonDto> getAll();

  boolean delete(String id);
}