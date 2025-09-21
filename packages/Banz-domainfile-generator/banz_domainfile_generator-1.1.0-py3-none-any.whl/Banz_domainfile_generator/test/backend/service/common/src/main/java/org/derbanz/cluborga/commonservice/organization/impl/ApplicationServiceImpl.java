package org.derbanz.cluborga.commonservice.organization.impl;

import io.quarkus.arc.Unremovable;
import jakarta.enterprise.context.ApplicationScoped;
import org.derbanz.cluborga.commonservice.organization.ApplicationService;

@Unremovable
@ApplicationScoped
public class ApplicationServiceImpl extends BaseApplicationServiceImpl implements ApplicationService {
}