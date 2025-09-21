package org.derbanz.cluborga.commonservice.organization.impl;

import io.quarkus.arc.Unremovable;
import jakarta.enterprise.context.ApplicationScoped;
import org.derbanz.cluborga.commonservice.organization.PersonService;

@Unremovable
@ApplicationScoped
public class PersonServiceImpl extends BasePersonServiceImpl implements PersonService {
}