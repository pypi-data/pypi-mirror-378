// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.transfer.BaseBto;
import org.derbanz.cluborga.domain.enums.MembershipStatus;

import java.util.Date;
import java.util.Objects;

public class MembershipCoreBto extends BaseBto {

  @NotEmpty
  private Date validFrom;

  private Date validTo;

  @NotEmpty
  private Boolean discount;

  @NotNull
  private MembershipStatus status;

  @NotEmpty
  private PersonBto person;


  public Date getValidFrom() {
    return validFrom;
  }

  public void setValidFrom(Date validFrom) {
    Objects.requireNonNull(validFrom, "ValidFrom cannot be null.");
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
    Objects.requireNonNull(discount, "Discount cannot be null.");
    this.discount = discount;
  }

  public MembershipStatus getStatus() {
    return status;
  }

  public void setStatus(MembershipStatus status) {
    Objects.requireNonNull(status, "Status cannot be null.");
    this.status = status;
  }


  public PersonBto getPerson() {
    return person;
  }

  public void setPerson(PersonBto person) {
    Objects.requireNonNull(person, "Person cannot be null.");
    this.person = person;
  }

}