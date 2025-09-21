// generated
package org.derbanz.cluborga.domain.model.organization.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import org.derbanz.cluborga.domain.model.organization.validation.impl.PersonValidatorImpl;

import java.lang.annotation.*;

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = PersonValidatorImpl.class)
@Documented
public @interface PersonValidator {

  String message() default "Error in PersonBto";

  Class<?>[] groups() default {};

  Class<? extends Payload>[] payload() default {};
}