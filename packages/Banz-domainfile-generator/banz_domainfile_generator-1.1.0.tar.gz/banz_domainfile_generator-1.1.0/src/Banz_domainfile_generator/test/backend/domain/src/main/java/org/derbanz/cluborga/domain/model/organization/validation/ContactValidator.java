// generated
package org.derbanz.cluborga.domain.model.organization.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import org.derbanz.cluborga.domain.model.organization.validation.impl.ContactValidatorImpl;

import java.lang.annotation.*;

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = ContactValidatorImpl.class)
@Documented
public @interface ContactValidator {

  String message() default "Error in ContactBto";

  Class<?>[] groups() default {};

  Class<? extends Payload>[] payload() default {};
}