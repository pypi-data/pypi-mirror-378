// generated
package org.derbanz.cluborga.logic.organization;

import jakarta.validation.ConstraintViolation;
import org.derbanz.cluborga.domain.model.organization.transfer.PaymentMethodBto;

import java.util.List;
import java.util.Set;

public interface BasePaymentMethodLogic {

  PaymentMethodBto instantiate();

  PaymentMethodBto get(String id);

  List<PaymentMethodBto> getList(List<String> ids);

  List<PaymentMethodBto> getAll();

  Set<ConstraintViolation<PaymentMethodBto>> validate(PaymentMethodBto bto);

  boolean save(PaymentMethodBto bto);

  boolean delete(PaymentMethodBto bto);

  boolean delete(String id);
}