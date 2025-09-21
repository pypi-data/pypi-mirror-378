// generated
package org.derbanz.cluborga.commonservice.organization;

import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.dto.PaymentMethodDto;

import java.util.List;

public interface BasePaymentMethodService {

  void validate(PaymentMethodDto dto) throws ValidationException;

  String save(PaymentMethodDto dto) throws ValidationException;

  PaymentMethodDto get(String id);

  List<PaymentMethodDto> getList(List<String> ids);

  List<PaymentMethodDto> getAll();

  boolean delete(String id);
}