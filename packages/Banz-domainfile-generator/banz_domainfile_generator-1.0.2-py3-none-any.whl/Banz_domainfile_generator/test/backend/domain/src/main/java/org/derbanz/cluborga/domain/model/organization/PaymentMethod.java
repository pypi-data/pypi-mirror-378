// generated
package org.derbanz.cluborga.domain.model.organization;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.AbstractBusinessObject;

import java.util.Date;

@Entity(
  name = "org.derbanz.cluborga.domain.model.organization.PaymentMethod"
)
@Table(
  name = "co_paymentmethod"
)
public class PaymentMethod extends AbstractBusinessObject {

  public static final String VALID_FROM = "validFrom";
  public static final String VALID_TO = "validTo";
  public static final String IBAN = "iban";
  public static final String BIC = "bic";
  public static final String BANK = "bank";
  public static final String SEPA_MANDATE = "sepaMandate";

  public static final String MEMBERSHIP = "membership";

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
  private String iban;

  @Basic
  @Access(AccessType.FIELD)
  private String bic;

  @Basic
  @Access(AccessType.FIELD)
  private String bank;

  @Basic
  @NotEmpty()
  @Access(AccessType.FIELD)
  private Boolean sepaMandate;

  @ManyToOne(fetch = FetchType.LAZY)
  @NotEmpty()
  private Membership membership;


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

  public String getIban() {
    return iban;
  }

  public void setIban(final String iban) {
    this.iban = iban;
  }

  public String getBic() {
    return bic;
  }

  public void setBic(final String bic) {
    this.bic = bic;
  }

  public String getBank() {
    return bank;
  }

  public void setBank(final String bank) {
    this.bank = bank;
  }

  public Boolean getSepaMandate() {
    return sepaMandate;
  }

  public void setSepaMandate(final Boolean sepaMandate) {
    this.sepaMandate = sepaMandate;
  }


  public Membership getMembership() {
    return membership;
  }

  public void setMembership(final Membership membership) {
    this.membership = membership;
  }

}