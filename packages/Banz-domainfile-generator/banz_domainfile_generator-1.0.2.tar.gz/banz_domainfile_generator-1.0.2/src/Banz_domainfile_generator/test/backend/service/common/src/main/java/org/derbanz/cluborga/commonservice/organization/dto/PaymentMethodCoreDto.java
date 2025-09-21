// generated
package org.derbanz.cluborga.commonservice.organization.dto;

import org.derbanz.cluborga.domain.base.dto.BaseDto;

import java.util.Date;

public class PaymentMethodCoreDto extends BaseDto {

  private Date validFrom;
  private Date validTo;
  private String iban;
  private String bic;
  private String bank;
  private Boolean sepaMandate;

  private MembershipDto membership;

  public Date getValidFrom() {
    return validFrom;
  }

  public void setValidFrom(Date validFrom) {
    this.validFrom = validFrom;
  }

  public Date getValidTo() {
    return validTo;
  }

  public void setValidTo(Date validTo) {
    this.validTo = validTo;
  }

  public String getIban() {
    return iban;
  }

  public void setIban(String iban) {
    this.iban = iban;
  }

  public String getBic() {
    return bic;
  }

  public void setBic(String bic) {
    this.bic = bic;
  }

  public String getBank() {
    return bank;
  }

  public void setBank(String bank) {
    this.bank = bank;
  }

  public Boolean getSepaMandate() {
    return sepaMandate;
  }

  public void setSepaMandate(Boolean sepaMandate) {
    this.sepaMandate = sepaMandate;
  }

  public MembershipDto getMembership() {
    return membership;
  }

  public void setMembership(MembershipDto membership) {
    this.membership = membership;
  }

}