// generated
package org.derbanz.cluborga.commonservice.organization.impl;

import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.BaseContactService;
import org.derbanz.cluborga.commonservice.organization.dto.ContactDto;
import org.derbanz.cluborga.commonservice.organization.util.ContactDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.ContactBto;
import org.derbanz.cluborga.logic.organization.ContactLogic;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class BaseContactServiceImpl implements BaseContactService {

  @Inject
  ContactLogic logic;
  @Inject
  ContactDtoMapper mapper;

  @Override
  public void validate(ContactDto dto) throws ValidationException {
    ContactBto bto = mapper.toBto(dto);
    Set<ConstraintViolation<ContactBto>> validationResult = logic.validate(bto);
    if (!validationResult.isEmpty()) {
      String message = validationResult.stream()
                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage())).collect(Collectors.joining("\n"));
      throw new ValidationException(message);
    }
  }

  @Override
  @Transactional
  public String save(ContactDto dto) throws ValidationException {
    ContactBto bto = mapper.toBto(dto);
    logic.save(bto);
    dto.setId(bto.getId());
    return dto.getId();
  }

  @Override
  public ContactDto get(String id) {
    ContactBto bto = logic.get(id);
    return mapper.toDto(bto);
  }

  @Override
  public List<ContactDto> getList(List<String> ids) {
    return logic.getList(ids).stream().map(mapper::toDto).toList();
  }

  @Override
  public List<ContactDto> getAll() {
    return logic.getAll().stream().map(mapper::toDto).toList();
  }

  @Override
  @Transactional
  public boolean delete(String id) {
    return logic.delete(id);
  }
}