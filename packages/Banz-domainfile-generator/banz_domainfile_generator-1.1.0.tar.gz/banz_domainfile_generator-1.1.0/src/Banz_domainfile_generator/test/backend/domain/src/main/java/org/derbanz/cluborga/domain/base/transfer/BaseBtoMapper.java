// generated
package org.derbanz.cluborga.domain.base.transfer;

import org.derbanz.cluborga.domain.base.AbstractBusinessObject;

public class BaseBtoMapper {

  protected void mapBasePropertiesToBto(AbstractBusinessObject bo, BaseBto bto) {
    bto.setCreation(bo.getCreation());
    bto.setCreationUser(bo.getCreationUser());
    bto.setLastUpdate(bo.getLastUpdate());
    bto.setLastUpdateUser(bo.getCreationUser());
    bto.setId(bo.getId().toString());
  }
}