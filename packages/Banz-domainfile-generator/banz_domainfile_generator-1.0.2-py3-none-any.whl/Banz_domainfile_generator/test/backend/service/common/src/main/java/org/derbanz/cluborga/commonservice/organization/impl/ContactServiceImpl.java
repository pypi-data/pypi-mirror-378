package org.derbanz.cluborga.commonservice.organization.impl;

import io.quarkus.arc.Unremovable;
import jakarta.enterprise.context.ApplicationScoped;
import org.derbanz.cluborga.commonservice.organization.ContactService;

@Unremovable
@ApplicationScoped
public class ContactServiceImpl extends BaseContactServiceImpl implements ContactService {
}