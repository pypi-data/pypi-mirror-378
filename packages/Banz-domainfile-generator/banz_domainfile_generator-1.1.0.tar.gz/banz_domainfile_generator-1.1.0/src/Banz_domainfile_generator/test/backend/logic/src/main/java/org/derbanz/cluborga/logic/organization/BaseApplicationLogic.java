// generated
package org.derbanz.cluborga.logic.organization;

import jakarta.validation.ConstraintViolation;
import org.derbanz.cluborga.domain.model.organization.transfer.ApplicationBto;

import java.util.List;
import java.util.Set;

public interface BaseApplicationLogic {

  ApplicationBto instantiate();

  ApplicationBto get(String id);

  List<ApplicationBto> getList(List<String> ids);

  List<ApplicationBto> getAll();

  Set<ConstraintViolation<ApplicationBto>> validate(ApplicationBto bto);

  boolean save(ApplicationBto bto);

  boolean delete(ApplicationBto bto);

  boolean delete(String id);
}