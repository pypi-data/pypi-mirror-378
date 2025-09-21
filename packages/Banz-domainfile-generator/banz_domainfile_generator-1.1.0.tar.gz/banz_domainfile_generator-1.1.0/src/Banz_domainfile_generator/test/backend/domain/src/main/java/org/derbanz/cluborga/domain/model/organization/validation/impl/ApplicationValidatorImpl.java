package org.derbanz.cluborga.domain.model.organization.validation.impl;

import jakarta.inject.Inject;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.derbanz.cluborga.domain.base.I18N;
import org.derbanz.cluborga.domain.model.organization.transfer.ApplicationBto;
import org.derbanz.cluborga.domain.model.organization.validation.ApplicationValidator;
import org.derbanz.cluborga.domain.model.organization.validation.ApplicationValidatorRule;

public class ApplicationValidatorImpl implements ConstraintValidator<ApplicationValidator, ApplicationBto> {

  @Inject
  I18N i18N;
  @Inject
  ApplicationValidatorRule validatorRule;

  @Override
  public void initialize(ApplicationValidator constraintAnnotation) {
  }

  @Override
  public boolean isValid(ApplicationBto applicationBto, ConstraintValidatorContext constraintValidatorContext) {
    return true;
  }
}