// generated
package org.derbanz.cluborga.domain.model.organization.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import org.derbanz.cluborga.domain.model.organization.validation.impl.MembershipValidatorImpl;

import java.lang.annotation.*;

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = MembershipValidatorImpl.class)
@Documented
public @interface MembershipValidator {

  String message() default "Error in MembershipBto";

  Class<?>[] groups() default {};

  Class<? extends Payload>[] payload() default {};
}