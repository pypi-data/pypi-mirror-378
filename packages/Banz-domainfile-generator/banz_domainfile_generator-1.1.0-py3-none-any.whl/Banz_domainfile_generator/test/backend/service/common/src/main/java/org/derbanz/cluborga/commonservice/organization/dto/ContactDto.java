package org.derbanz.cluborga.commonservice.organization.dto;

public class ContactDto extends ContactCoreDto {

  @Override
  public boolean equals(Object object) {
    if (object == null) {
      return false;
    }
    if (object.getClass() != this.getClass()) {
      return false;
    }
    final ContactDto dto = (ContactDto) object;
    if (dto.getId() == null) {
      return object == this;
    } else {
      return this.getId().equals(dto.getId());
    }
  }
}