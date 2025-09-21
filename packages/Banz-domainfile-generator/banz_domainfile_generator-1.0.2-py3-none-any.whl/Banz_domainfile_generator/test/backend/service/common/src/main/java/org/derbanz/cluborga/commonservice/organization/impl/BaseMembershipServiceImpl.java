// generated
package org.derbanz.cluborga.commonservice.organization.impl;

import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.BaseMembershipService;
import org.derbanz.cluborga.commonservice.organization.dto.MembershipDto;
import org.derbanz.cluborga.commonservice.organization.util.MembershipDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.MembershipBto;
import org.derbanz.cluborga.logic.organization.MembershipLogic;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class BaseMembershipServiceImpl implements BaseMembershipService {

  @Inject
  MembershipLogic logic;
  @Inject
  MembershipDtoMapper mapper;

  @Override
  public void validate(MembershipDto dto) throws ValidationException {
    MembershipBto bto = mapper.toBto(dto);
    Set<ConstraintViolation<MembershipBto>> validationResult = logic.validate(bto);
    if (!validationResult.isEmpty()) {
      String message = validationResult.stream()
                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage())).collect(Collectors.joining("\n"));
      throw new ValidationException(message);
    }
  }

  @Override
  @Transactional
  public String save(MembershipDto dto) throws ValidationException {
    MembershipBto bto = mapper.toBto(dto);
    logic.save(bto);
    dto.setId(bto.getId());
    return dto.getId();
  }

  @Override
  public MembershipDto get(String id) {
    MembershipBto bto = logic.get(id);
    return mapper.toDto(bto);
  }

  @Override
  public List<MembershipDto> getList(List<String> ids) {
    return logic.getList(ids).stream().map(mapper::toDto).toList();
  }

  @Override
  public List<MembershipDto> getAll() {
    return logic.getAll().stream().map(mapper::toDto).toList();
  }

  @Override
  @Transactional
  public boolean delete(String id) {
    return logic.delete(id);
  }
}