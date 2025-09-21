// generated
package org.derbanz.cluborga.commonservice.organization.dto;

import org.derbanz.cluborga.domain.base.dto.BaseDto;
import org.derbanz.cluborga.domain.enums.MembershipStatus;

import java.util.Date;

public class MembershipCoreDto extends BaseDto {

  private Date validFrom;
  private Date validTo;
  private Boolean discount;
  private MembershipStatus status;

  private PersonDto person;

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

  public Boolean getDiscount() {
    return discount;
  }

  public void setDiscount(Boolean discount) {
    this.discount = discount;
  }

  public MembershipStatus getStatus() {
    return status;
  }

  public void setStatus(MembershipStatus status) {
    this.status = status;
  }

  public PersonDto getPerson() {
    return person;
  }

  public void setPerson(PersonDto person) {
    this.person = person;
  }

}