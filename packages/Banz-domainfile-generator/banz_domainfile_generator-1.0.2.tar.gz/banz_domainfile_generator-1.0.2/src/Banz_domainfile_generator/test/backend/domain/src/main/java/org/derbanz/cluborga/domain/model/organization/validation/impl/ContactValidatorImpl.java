package org.derbanz.cluborga.domain.model.organization.validation.impl;

import jakarta.inject.Inject;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.derbanz.cluborga.domain.base.I18N;
import org.derbanz.cluborga.domain.model.organization.transfer.ContactBto;
import org.derbanz.cluborga.domain.model.organization.validation.ContactValidator;
import org.derbanz.cluborga.domain.model.organization.validation.ContactValidatorRule;

public class ContactValidatorImpl implements ConstraintValidator<ContactValidator, ContactBto> {

  @Inject
  I18N i18N;
  @Inject
  ContactValidatorRule validatorRule;

  @Override
  public void initialize(ContactValidator constraintAnnotation) {
  }

  @Override
  public boolean isValid(ContactBto contactBto, ConstraintValidatorContext constraintValidatorContext) {
    return true;
  }
}