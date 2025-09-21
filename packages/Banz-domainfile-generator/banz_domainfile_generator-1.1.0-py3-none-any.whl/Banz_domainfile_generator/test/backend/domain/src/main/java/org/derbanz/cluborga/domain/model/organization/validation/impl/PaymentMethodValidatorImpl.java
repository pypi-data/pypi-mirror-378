package org.derbanz.cluborga.domain.model.organization.validation.impl;

import jakarta.inject.Inject;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.derbanz.cluborga.domain.base.I18N;
import org.derbanz.cluborga.domain.model.organization.transfer.PaymentMethodBto;
import org.derbanz.cluborga.domain.model.organization.validation.PaymentMethodValidator;
import org.derbanz.cluborga.domain.model.organization.validation.PaymentMethodValidatorRule;

public class PaymentMethodValidatorImpl implements ConstraintValidator<PaymentMethodValidator, PaymentMethodBto> {

  @Inject
  I18N i18N;
  @Inject
  PaymentMethodValidatorRule validatorRule;

  @Override
  public void initialize(PaymentMethodValidator constraintAnnotation) {
  }

  @Override
  public boolean isValid(PaymentMethodBto paymentmethodBto, ConstraintValidatorContext constraintValidatorContext) {
    return true;
  }
}