// generated
package org.derbanz.cluborga.commonservice.organization;

import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.dto.ContactDto;

import java.util.List;

public interface BaseContactService {

  void validate(ContactDto dto) throws ValidationException;

  String save(ContactDto dto) throws ValidationException;

  ContactDto get(String id);

  List<ContactDto> getList(List<String> ids);

  List<ContactDto> getAll();

  boolean delete(String id);
}