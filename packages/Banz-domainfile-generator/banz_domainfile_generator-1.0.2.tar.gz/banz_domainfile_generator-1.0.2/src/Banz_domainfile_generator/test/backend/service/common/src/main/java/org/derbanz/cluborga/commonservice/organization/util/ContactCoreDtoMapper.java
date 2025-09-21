// generated
package org.derbanz.cluborga.commonservice.organization.util;

import jakarta.inject.Inject;
import org.derbanz.cluborga.domain.base.util.BaseDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.ContactBto;

public class ContactCoreDtoMapper extends BaseDtoMapper {

  @Inject
  PersonDtoMapper personDtoMapper;

  private void mapPropertiesToBto(ContactCoreDto dto, ContactBto bto) {
    mapBaseDtoToBto(dto, bto);

    bto.setValidFrom(dto.getValidFrom());
    bto.setValidTo(dto.getValidTo());
    bto.setType(dto.getType());
    bto.setStreet(dto.getStreet());
    bto.setNumber(dto.getNumber());
    bto.setNumberSuffix(dto.getNumberSuffix());
    bto.setPostbox(dto.getPostbox());
    bto.setZip(dto.getZip());
    bto.setCity(dto.getCity());
    bto.setCountry(dto.getCountry());
    bto.setCountryCode(dto.getCountryCode());
    bto.setPhoneNumber(dto.getPhoneNumber());
    bto.setEmail(dto.getEmail());
  }

  private void mapPropertiesToDto(ContactBto bto, ContactCoreDto dto) {
    mapBaseBtoToDto(bto, dto);

    dto.setValidFrom(bto.getValidFrom());
    dto.setValidTo(bto.getValidTo());
    dto.setType(bto.getType());
    dto.setStreet(bto.getStreet());
    dto.setNumber(bto.getNumber());
    dto.setNumberSuffix(bto.getNumberSuffix());
    dto.setPostbox(bto.getPostbox());
    dto.setZip(bto.getZip());
    dto.setCity(bto.getCity());
    dto.setCountry(bto.getCountry());
    dto.setCountryCode(bto.getCountryCode());
    dto.setPhoneNumber(bto.getPhoneNumber());
    dto.setEmail(bto.getEmail());
  }

  public void mapToBto(ContactCoreDto dto, ContactBto bto) {
    if (dto != null) {
      mapPropertiesToBto(dto, bto);
      if (dto.getPerson() != null) {
        bto.setPerson(personDtoMapper.toBto(dto.getPerson()));
      }
    }
  }

  public ContactBto toBto(ContactCoreDto dto) {
    ContactBto bto = new ContactBto();
    mapToBto(dto, bto);
    return bto;
  }

  public void mapToDto(ContactBto bto, ContactCoreDto dto) {
    if (bto != null) {
      mapPropertiesToDto(bto, dto);
      if (bto.getPerson() != null) {
        dto.setPerson(personDtoMapper.toDto(bto.getPerson()));
      }
    }
  }

  public ContactDto toDto(ContactBto bto) {
    ContactDto dto = new ContactDto();
    mapToDto(bto, dto);
    return dto;
  }
}