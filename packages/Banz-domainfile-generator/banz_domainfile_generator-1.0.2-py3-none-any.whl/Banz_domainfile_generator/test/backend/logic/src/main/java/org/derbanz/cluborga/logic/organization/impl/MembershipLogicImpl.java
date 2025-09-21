package org.derbanz.cluborga.logic.organization.impl;

import io.quarkus.arc.Unremovable;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Specializes;
import org.derbanz.cluborga.logic.organization.MembershipLogic;

@Unremovable
@Specializes
@ApplicationScoped
public class MembershipLogicImpl extends BaseMembershipLogicImpl implements MembershipLogic {
}