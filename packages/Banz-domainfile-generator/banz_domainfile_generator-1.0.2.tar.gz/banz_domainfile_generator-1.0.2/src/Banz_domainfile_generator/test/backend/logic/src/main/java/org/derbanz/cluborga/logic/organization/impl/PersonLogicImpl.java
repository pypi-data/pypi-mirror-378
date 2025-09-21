package org.derbanz.cluborga.logic.organization.impl;

import io.quarkus.arc.Unremovable;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.inject.Specializes;
import org.derbanz.cluborga.logic.organization.PersonLogic;

@Unremovable
@Specializes
@ApplicationScoped
public class PersonLogicImpl extends BasePersonLogicImpl implements PersonLogic {
}