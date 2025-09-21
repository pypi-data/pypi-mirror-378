// generated
package org.derbanz.cluborga.domain.model.organization.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import org.derbanz.cluborga.domain.model.organization.validation.impl.ApplicationValidatorImpl;

import java.lang.annotation.*;

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = ApplicationValidatorImpl.class)
@Documented
public @interface ApplicationValidator {

  String message() default "Error in ApplicationBto";

  Class<?>[] groups() default {};

  Class<? extends Payload>[] payload() default {};
}