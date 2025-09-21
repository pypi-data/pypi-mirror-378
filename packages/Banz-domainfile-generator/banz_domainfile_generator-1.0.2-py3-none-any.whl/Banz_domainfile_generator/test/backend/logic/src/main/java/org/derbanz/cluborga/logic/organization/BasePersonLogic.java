// generated
package org.derbanz.cluborga.logic.organization;

import jakarta.validation.ConstraintViolation;
import org.derbanz.cluborga.domain.model.organization.transfer.PersonBto;

import java.util.List;
import java.util.Set;

public interface BasePersonLogic {

  PersonBto instantiate();

  PersonBto get(String id);

  List<PersonBto> getList(List<String> ids);

  List<PersonBto> getAll();

  Set<ConstraintViolation<PersonBto>> validate(PersonBto bto);

  boolean save(PersonBto bto);

  boolean delete(PersonBto bto);

  boolean delete(String id);
}