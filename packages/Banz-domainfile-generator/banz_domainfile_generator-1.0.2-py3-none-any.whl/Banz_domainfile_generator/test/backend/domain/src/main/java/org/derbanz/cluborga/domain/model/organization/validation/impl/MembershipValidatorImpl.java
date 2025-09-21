package org.derbanz.cluborga.domain.model.organization.validation.impl;

import jakarta.inject.Inject;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import org.derbanz.cluborga.domain.base.I18N;
import org.derbanz.cluborga.domain.model.organization.transfer.MembershipBto;
import org.derbanz.cluborga.domain.model.organization.validation.MembershipValidator;
import org.derbanz.cluborga.domain.model.organization.validation.MembershipValidatorRule;

public class MembershipValidatorImpl implements ConstraintValidator<MembershipValidator, MembershipBto> {

  @Inject
  I18N i18N;
  @Inject
  MembershipValidatorRule validatorRule;

  @Override
  public void initialize(MembershipValidator constraintAnnotation) {
  }

  @Override
  public boolean isValid(MembershipBto membershipBto, ConstraintValidatorContext constraintValidatorContext) {
    return true;
  }
}