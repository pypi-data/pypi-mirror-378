// generated
package org.derbanz.cluborga.domain.model.organization;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.AbstractBusinessObject;
import org.derbanz.cluborga.domain.enums.MembershipStatus;

import java.util.Date;

@Entity(
  name = "org.derbanz.cluborga.domain.model.organization.Membership"
)
@Table(
  name = "co_membership"
)
public class Membership extends AbstractBusinessObject {

  public static final String VALID_FROM = "validFrom";
  public static final String VALID_TO = "validTo";
  public static final String DISCOUNT = "discount";
  public static final String STATUS = "status";

  public static final String PERSON = "person";

  @Basic
  @NotEmpty()
  @Access(AccessType.FIELD)
  private Date validFrom;

  @Basic
  @Access(AccessType.FIELD)
  private Date validTo;

  @Basic
  @NotEmpty()
  @Access(AccessType.FIELD)
  private Boolean discount;

  @Basic
  @NotEmpty()
  @Enumerated(EnumType.STRING)
  @Access(AccessType.FIELD)
  private MembershipStatus status;

  @ManyToOne(fetch = FetchType.LAZY)
  @NotEmpty()
  private Person person;


  public Date getValidFrom() {
    return validFrom;
  }

  public void setValidFrom(final Date validFrom) {
    this.validFrom = validFrom;
  }

  public Date getValidTo() {
    return validTo;
  }

  public void setValidTo(final Date validTo) {
    this.validTo = validTo;
  }

  public Boolean getDiscount() {
    return discount;
  }

  public void setDiscount(final Boolean discount) {
    this.discount = discount;
  }

  public MembershipStatus getStatus() {
    return status;
  }

  public void setStatus(final MembershipStatus status) {
    this.status = status;
  }


  public Person getPerson() {
    return person;
  }

  public void setPerson(final Person person) {
    this.person = person;
  }

}