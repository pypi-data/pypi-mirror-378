package org.derbanz.cluborga.commonservice.organization.impl;

import io.quarkus.arc.Unremovable;
import jakarta.enterprise.context.ApplicationScoped;
import org.derbanz.cluborga.commonservice.organization.MembershipService;

@Unremovable
@ApplicationScoped
public class MembershipServiceImpl extends BaseMembershipServiceImpl implements MembershipService {
}