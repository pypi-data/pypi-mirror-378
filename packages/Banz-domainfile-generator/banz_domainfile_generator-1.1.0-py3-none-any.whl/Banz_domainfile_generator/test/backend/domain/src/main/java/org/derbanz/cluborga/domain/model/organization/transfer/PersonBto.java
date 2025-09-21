package org.derbanz.cluborga.domain.model.organization.transfer;

import org.derbanz.cluborga.domain.model.organization.validation.PersonValidator;

@PersonValidator
public class PersonBto extends PersonCoreBto {

  @Override
  public boolean equals(Object object) {
    if (object == null) {
      return false;
    }
    if (object.getClass() != this.getClass()) {
      return false;
    }
    final PersonBto bto = (PersonBto) object;
    if (bto.getId() == null) {
      return object == this;
    } else {
      return this.getId().equals(bto.getId());
    }
  }
}