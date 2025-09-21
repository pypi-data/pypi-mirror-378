// generated
package org.derbanz.cluborga.commonservice.organization.impl;

import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.BaseApplicationService;
import org.derbanz.cluborga.commonservice.organization.dto.ApplicationDto;
import org.derbanz.cluborga.commonservice.organization.util.ApplicationDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.ApplicationBto;
import org.derbanz.cluborga.logic.organization.ApplicationLogic;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class BaseApplicationServiceImpl implements BaseApplicationService {

  @Inject
  ApplicationLogic logic;
  @Inject
  ApplicationDtoMapper mapper;

  @Override
  public void validate(ApplicationDto dto) throws ValidationException {
    ApplicationBto bto = mapper.toBto(dto);
    Set<ConstraintViolation<ApplicationBto>> validationResult = logic.validate(bto);
    if (!validationResult.isEmpty()) {
      String message = validationResult.stream()
                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage())).collect(Collectors.joining("\n"));
      throw new ValidationException(message);
    }
  }

  @Override
  @Transactional
  public String save(ApplicationDto dto) throws ValidationException {
    ApplicationBto bto = mapper.toBto(dto);
    logic.save(bto);
    dto.setId(bto.getId());
    return dto.getId();
  }

  @Override
  public ApplicationDto get(String id) {
    ApplicationBto bto = logic.get(id);
    return mapper.toDto(bto);
  }

  @Override
  public List<ApplicationDto> getList(List<String> ids) {
    return logic.getList(ids).stream().map(mapper::toDto).toList();
  }

  @Override
  public List<ApplicationDto> getAll() {
    return logic.getAll().stream().map(mapper::toDto).toList();
  }

  @Override
  @Transactional
  public boolean delete(String id) {
    return logic.delete(id);
  }
}