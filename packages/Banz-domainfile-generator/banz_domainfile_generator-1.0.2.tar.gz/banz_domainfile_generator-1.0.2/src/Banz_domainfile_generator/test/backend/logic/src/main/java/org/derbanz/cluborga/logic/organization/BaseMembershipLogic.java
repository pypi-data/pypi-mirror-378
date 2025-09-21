// generated
package org.derbanz.cluborga.logic.organization;

import jakarta.validation.ConstraintViolation;
import org.derbanz.cluborga.domain.model.organization.transfer.MembershipBto;

import java.util.List;
import java.util.Set;

public interface BaseMembershipLogic {

  MembershipBto instantiate();

  MembershipBto get(String id);

  List<MembershipBto> getList(List<String> ids);

  List<MembershipBto> getAll();

  Set<ConstraintViolation<MembershipBto>> validate(MembershipBto bto);

  boolean save(MembershipBto bto);

  boolean delete(MembershipBto bto);

  boolean delete(String id);
}