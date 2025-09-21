// generated
package org.derbanz.cluborga.domain.model.organization.validation;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;
import org.derbanz.cluborga.domain.model.organization.validation.impl.PaymentMethodValidatorImpl;

import java.lang.annotation.*;

@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = PaymentMethodValidatorImpl.class)
@Documented
public @interface PaymentMethodValidator {

  String message() default "Error in PaymentMethodBto";

  Class<?>[] groups() default {};

  Class<? extends Payload>[] payload() default {};
}