// generated
package org.derbanz.cluborga.commonservice.organization.impl;

import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.BasePaymentMethodService;
import org.derbanz.cluborga.commonservice.organization.dto.PaymentMethodDto;
import org.derbanz.cluborga.commonservice.organization.util.PaymentMethodDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.PaymentMethodBto;
import org.derbanz.cluborga.logic.organization.PaymentMethodLogic;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class BasePaymentMethodServiceImpl implements BasePaymentMethodService {

  @Inject
  PaymentMethodLogic logic;
  @Inject
  PaymentMethodDtoMapper mapper;

  @Override
  public void validate(PaymentMethodDto dto) throws ValidationException {
    PaymentMethodBto bto = mapper.toBto(dto);
    Set<ConstraintViolation<PaymentMethodBto>> validationResult = logic.validate(bto);
    if (!validationResult.isEmpty()) {
      String message = validationResult.stream()
                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage())).collect(Collectors.joining("\n"));
      throw new ValidationException(message);
    }
  }

  @Override
  @Transactional
  public String save(PaymentMethodDto dto) throws ValidationException {
    PaymentMethodBto bto = mapper.toBto(dto);
    logic.save(bto);
    dto.setId(bto.getId());
    return dto.getId();
  }

  @Override
  public PaymentMethodDto get(String id) {
    PaymentMethodBto bto = logic.get(id);
    return mapper.toDto(bto);
  }

  @Override
  public List<PaymentMethodDto> getList(List<String> ids) {
    return logic.getList(ids).stream().map(mapper::toDto).toList();
  }

  @Override
  public List<PaymentMethodDto> getAll() {
    return logic.getAll().stream().map(mapper::toDto).toList();
  }

  @Override
  @Transactional
  public boolean delete(String id) {
    return logic.delete(id);
  }
}