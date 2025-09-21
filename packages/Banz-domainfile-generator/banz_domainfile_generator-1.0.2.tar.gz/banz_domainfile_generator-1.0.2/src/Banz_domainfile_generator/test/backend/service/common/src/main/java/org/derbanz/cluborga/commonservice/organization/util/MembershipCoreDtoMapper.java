// generated
package org.derbanz.cluborga.commonservice.organization.util;

import jakarta.inject.Inject;
import org.derbanz.cluborga.domain.base.util.BaseDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.MembershipBto;

public class MembershipCoreDtoMapper extends BaseDtoMapper {

  @Inject
  PersonDtoMapper personDtoMapper;

  private void mapPropertiesToBto(MembershipCoreDto dto, MembershipBto bto) {
    mapBaseDtoToBto(dto, bto);

    bto.setValidFrom(dto.getValidFrom());
    bto.setValidTo(dto.getValidTo());
    bto.setDiscount(dto.getDiscount());
    bto.setStatus(dto.getStatus());
  }

  private void mapPropertiesToDto(MembershipBto bto, MembershipCoreDto dto) {
    mapBaseBtoToDto(bto, dto);

    dto.setValidFrom(bto.getValidFrom());
    dto.setValidTo(bto.getValidTo());
    dto.setDiscount(bto.getDiscount());
    dto.setStatus(bto.getStatus());
  }

  public void mapToBto(MembershipCoreDto dto, MembershipBto bto) {
    if (dto != null) {
      mapPropertiesToBto(dto, bto);
      if (dto.getPerson() != null) {
        bto.setPerson(personDtoMapper.toBto(dto.getPerson()));
      }
    }
  }

  public MembershipBto toBto(MembershipCoreDto dto) {
    MembershipBto bto = new MembershipBto();
    mapToBto(dto, bto);
    return bto;
  }

  public void mapToDto(MembershipBto bto, MembershipCoreDto dto) {
    if (bto != null) {
      mapPropertiesToDto(bto, dto);
      if (bto.getPerson() != null) {
        dto.setPerson(personDtoMapper.toDto(bto.getPerson()));
      }
    }
  }

  public MembershipDto toDto(MembershipBto bto) {
    MembershipDto dto = new MembershipDto();
    mapToDto(bto, dto);
    return dto;
  }
}