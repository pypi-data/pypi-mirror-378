package org.derbanz.cluborga.commonservice.organization.dto;

public class PaymentMethodDto extends PaymentMethodCoreDto {

  @Override
  public boolean equals(Object object) {
    if (object == null) {
      return false;
    }
    if (object.getClass() != this.getClass()) {
      return false;
    }
    final PaymentMethodDto dto = (PaymentMethodDto) object;
    if (dto.getId() == null) {
      return object == this;
    } else {
      return this.getId().equals(dto.getId());
    }
  }
}