// generated
package org.derbanz.cluborga.logic.organization;

import jakarta.validation.ConstraintViolation;
import org.derbanz.cluborga.domain.model.organization.transfer.ContactBto;

import java.util.List;
import java.util.Set;

public interface BaseContactLogic {

  ContactBto instantiate();

  ContactBto get(String id);

  List<ContactBto> getList(List<String> ids);

  List<ContactBto> getAll();

  Set<ConstraintViolation<ContactBto>> validate(ContactBto bto);

  boolean save(ContactBto bto);

  boolean delete(ContactBto bto);

  boolean delete(String id);
}