// generated
package org.derbanz.cluborga.commonservice.organization;

import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.dto.ApplicationDto;

import java.util.List;

public interface BaseApplicationService {

  void validate(ApplicationDto dto) throws ValidationException;

  String save(ApplicationDto dto) throws ValidationException;

  ApplicationDto get(String id);

  List<ApplicationDto> getList(List<String> ids);

  List<ApplicationDto> getAll();

  boolean delete(String id);
}