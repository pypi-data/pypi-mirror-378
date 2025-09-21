// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.validation.constraints.NotEmpty;
import org.derbanz.cluborga.domain.base.transfer.BaseBto;

import java.util.Date;
import java.util.Objects;

public class PaymentMethodCoreBto extends BaseBto {

  @NotEmpty
  private Date validFrom;

  private Date validTo;

  @NotEmpty
  private String iban;

  private String bic;

  private String bank;

  @NotEmpty
  private Boolean sepaMandate;

  @NotEmpty
  private MembershipBto membership;


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

  public String getIban() {
    return iban;
  }

  public void setIban(String iban) {
    Objects.requireNonNull(iban, "Iban cannot be null.");
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
    Objects.requireNonNull(sepaMandate, "SepaMandate cannot be null.");
    this.sepaMandate = sepaMandate;
  }


  public MembershipBto getMembership() {
    return membership;
  }

  public void setMembership(MembershipBto membership) {
    Objects.requireNonNull(membership, "Membership cannot be null.");
    this.membership = membership;
  }

}