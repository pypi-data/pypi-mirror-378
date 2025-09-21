// generated
package org.derbanz.cluborga.commonservice.organization.util;

import jakarta.inject.Inject;
import org.derbanz.cluborga.commonservice.organization.dto.ApplicationDto;
import org.derbanz.cluborga.domain.base.util.BaseDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.ApplicationBto;

public class ApplicationCoreDtoMapper extends BaseDtoMapper {

  @Inject
  MembershipDtoMapper membershipDtoMapper;

  private void mapPropertiesToBto(ApplicationDto dto, ApplicationBto bto) {
    mapBaseDtoToBto(dto, bto);

    bto.setApplicationDate(dto.getApplicationDate());
    bto.setDateOfReply(dto.getDateOfReply());
    bto.setStatus(dto.getStatus());
  }

  private void mapPropertiesToDto(ApplicationBto bto, ApplicationDto dto) {
    mapBaseBtoToDto(bto, dto);

    dto.setApplicationDate(bto.getApplicationDate());
    dto.setDateOfReply(bto.getDateOfReply());
    dto.setStatus(bto.getStatus());
  }

  public void mapToBto(ApplicationDto dto, ApplicationBto bto) {
    if (dto != null) {
      mapPropertiesToBto(dto, bto);
      if (dto.getMembership() != null) {
        bto.setMembership(membershipDtoMapper.toBto(dto.getMembership()));
      }
    }
  }

  public ApplicationBto toBto(ApplicationDto dto) {
    ApplicationBto bto = new ApplicationBto();
    mapToBto(dto, bto);
    return bto;
  }

  public void mapToDto(ApplicationBto bto, ApplicationDto dto) {
    if (bto != null) {
      mapPropertiesToDto(bto, dto);
      if (bto.getMembership() != null) {
        dto.setMembership(membershipDtoMapper.toDto(bto.getMembership()));
      }
    }
  }

  public ApplicationDto toDto(ApplicationBto bto) {
    ApplicationDto dto = new ApplicationDto();
    mapToDto(bto, dto);
    return dto;
  }
}