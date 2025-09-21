// generated
package org.derbanz.cluborga.domain.base.util;

import org.derbanz.cluborga.domain.base.dto.BaseDto;

import org.derbanz.cluborga.domain.base.transfer.BaseBto;

public class BaseDtoMapper {

  protected void mapBaseBtoToDto(BaseBto bto, BaseDto dto) {
    dto.setId(bto.getId());
    dto.setCreation(bto.getCreation());
    dto.setCreationUser(bto.getCreationUser());
    dto.setLastUpdate(bto.getLastUpdate());
    dto.setLastUpdateUser(bto.getCreationUser());
  }

  protected void mapBaseDtoToBto(BaseDto bto, BaseBto dto) {
    bto.setId(dto.getId());
    bto.setCreation(dto.getCreation());
    bto.setCreationUser(dto.getCreationUser());
    bto.setLastUpdate(dto.getLastUpdate());
    bto.setLastUpdateUser(dto.getCreationUser());
  }
}