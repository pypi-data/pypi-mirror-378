// generated
package org.derbanz.cluborga.commonservice.organization.util;

import jakarta.inject.Inject;
import org.derbanz.cluborga.commonservice.organization.dto.PersonDto;
import org.derbanz.cluborga.domain.base.util.BaseDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.PersonBto;

import java.util.List;

public class PersonCoreDtoMapper extends BaseDtoMapper {

  @Inject
  ContactDtoMapper contactDtoMapper;
  @Inject
  MembershipDtoMapper membershipDtoMapper;

  private void mapPropertiesToBto(PersonDto dto, PersonBto bto) {
    mapBaseDtoToBto(dto, bto);

    bto.setName(dto.getName());
    bto.setFirstName(dto.getFirstName());
    bto.setDateOfBirth(dto.getDateOfBirth());
    bto.setGender(dto.getGender());
  }

  private void mapPropertiesToDto(PersonBto bto, PersonDto dto) {
    mapBaseBtoToDto(bto, dto);

    dto.setName(bto.getName());
    dto.setFirstName(bto.getFirstName());
    dto.setDateOfBirth(bto.getDateOfBirth());
    dto.setGender(bto.getGender());
  }

  public void mapToBto(PersonDto dto, PersonBto bto) {
    if (dto != null) {
      mapPropertiesToBto(dto, bto);
      bto.setMemberships(dto.getMemberships().stream().map(membershipDtoMapper::toBto).toList());
      bto.setContacts(dto.getContacts().stream().map(contactDtoMapper::toBto).toList());
    }
  }

  public PersonBto toBto(PersonDto dto) {
    PersonBto bto = new PersonBto();
    mapToBto(dto, bto);
    return bto;
  }

  public void mapToDto(PersonBto bto, PersonDto dto) {
    if (bto != null) {
      mapPropertiesToDto(bto, dto);
      dto.setMemberships(bto.getMemberships().stream().map(membershipDtoMapper::toDto).toList());
      dto.setContacts(bto.getContacts().stream().map(contactDtoMapper::toDto).toList());
    }
  }

  public PersonDto toDto(PersonBto bto) {
    PersonDto dto = new PersonDto();
    mapToDto(bto, dto);
    return dto;
  }
}