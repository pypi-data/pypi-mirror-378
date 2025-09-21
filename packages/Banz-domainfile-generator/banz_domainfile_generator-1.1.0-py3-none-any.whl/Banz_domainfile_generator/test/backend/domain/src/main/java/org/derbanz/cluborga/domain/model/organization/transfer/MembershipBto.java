package org.derbanz.cluborga.domain.model.organization.transfer;

import org.derbanz.cluborga.domain.model.organization.validation.MembershipValidator;

@MembershipValidator
public class MembershipBto extends MembershipCoreBto {

  @Override
  public boolean equals(Object object) {
    if (object == null) {
      return false;
    }
    if (object.getClass() != this.getClass()) {
      return false;
    }
    final MembershipBto bto = (MembershipBto) object;
    if (bto.getId() == null) {
      return object == this;
    } else {
      return this.getId().equals(bto.getId());
    }
  }
}