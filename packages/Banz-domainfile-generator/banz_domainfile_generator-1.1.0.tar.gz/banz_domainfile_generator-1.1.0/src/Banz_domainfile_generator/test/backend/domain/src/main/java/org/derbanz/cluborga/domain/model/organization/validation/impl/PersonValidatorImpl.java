package org.derbanz.cluborga.domain.model.organization.validation.impl;

import jakarta.inject.Inject;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.derbanz.cluborga.domain.base.I18N;
import org.derbanz.cluborga.domain.model.organization.transfer.PersonBto;
import org.derbanz.cluborga.domain.model.organization.validation.PersonValidator;
import org.derbanz.cluborga.domain.model.organization.validation.PersonValidatorRule;

public class PersonValidatorImpl implements ConstraintValidator<PersonValidator, PersonBto> {

  @Inject
  I18N i18N;
  @Inject
  PersonValidatorRule validatorRule;

  @Override
  public void initialize(PersonValidator constraintAnnotation) {
  }

  @Override
  public boolean isValid(PersonBto personBto, ConstraintValidatorContext constraintValidatorContext) {
    return true;
  }
}