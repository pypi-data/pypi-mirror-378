// generated
package org.derbanz.cluborga.commonservice.organization.util;

import jakarta.inject.Inject;
import org.derbanz.cluborga.commonservice.organization.dto.PaymentMethodDto;
import org.derbanz.cluborga.domain.base.util.BaseDtoMapper;
import org.derbanz.cluborga.domain.model.organization.transfer.PaymentMethodBto;

public class PaymentMethodCoreDtoMapper extends BaseDtoMapper {

  @Inject
  MembershipDtoMapper membershipDtoMapper;

  private void mapPropertiesToBto(PaymentMethodDto dto, PaymentMethodBto bto) {
    mapBaseDtoToBto(dto, bto);

    bto.setValidFrom(dto.getValidFrom());
    bto.setValidTo(dto.getValidTo());
    bto.setIban(dto.getIban());
    bto.setBic(dto.getBic());
    bto.setBank(dto.getBank());
    bto.setSepaMandate(dto.getSepaMandate());
  }

  private void mapPropertiesToDto(PaymentMethodBto bto, PaymentMethodDto dto) {
    mapBaseBtoToDto(bto, dto);

    dto.setValidFrom(bto.getValidFrom());
    dto.setValidTo(bto.getValidTo());
    dto.setIban(bto.getIban());
    dto.setBic(bto.getBic());
    dto.setBank(bto.getBank());
    dto.setSepaMandate(bto.getSepaMandate());
  }

  public void mapToBto(PaymentMethodDto dto, PaymentMethodBto bto) {
    if (dto != null) {
      mapPropertiesToBto(dto, bto);
      if (dto.getMembership() != null) {
        bto.setMembership(membershipDtoMapper.toBto(dto.getMembership()));
      }
    }
  }

  public PaymentMethodBto toBto(PaymentMethodDto dto) {
    PaymentMethodBto bto = new PaymentMethodBto();
    mapToBto(dto, bto);
    return bto;
  }

  public void mapToDto(PaymentMethodBto bto, PaymentMethodDto dto) {
    if (bto != null) {
      mapPropertiesToDto(bto, dto);
      if (bto.getMembership() != null) {
        dto.setMembership(membershipDtoMapper.toDto(bto.getMembership()));
      }
    }
  }

  public PaymentMethodDto toDto(PaymentMethodBto bto) {
    PaymentMethodDto dto = new PaymentMethodDto();
    mapToDto(bto, dto);
    return dto;
  }
}