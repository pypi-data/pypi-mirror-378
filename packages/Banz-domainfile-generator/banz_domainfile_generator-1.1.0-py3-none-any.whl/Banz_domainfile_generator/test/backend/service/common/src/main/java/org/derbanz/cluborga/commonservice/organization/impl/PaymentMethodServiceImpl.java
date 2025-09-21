package org.derbanz.cluborga.commonservice.organization.impl;

import io.quarkus.arc.Unremovable;
import jakarta.enterprise.context.ApplicationScoped;
import org.derbanz.cluborga.commonservice.organization.PaymentMethodService;

@Unremovable
@ApplicationScoped
public class PaymentMethodServiceImpl extends BasePaymentMethodServiceImpl implements PaymentMethodService {
}