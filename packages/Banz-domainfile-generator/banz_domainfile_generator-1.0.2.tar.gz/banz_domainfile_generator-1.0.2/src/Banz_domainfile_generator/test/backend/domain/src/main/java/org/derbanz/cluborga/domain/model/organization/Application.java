// generated
package org.derbanz.cluborga.domain.model.organization;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.AbstractBusinessObject;
import org.derbanz.cluborga.domain.enums.Status;

import java.util.Date;

@Entity(
  name = "org.derbanz.cluborga.domain.model.organization.Application"
)
@Table(
  name = "co_application"
)
public class Application extends AbstractBusinessObject {

  public static final String APPLICATION_DATE = "applicationDate";
  public static final String DATE_OF_REPLY = "dateOfReply";
  public static final String STATUS = "status";

  public static final String MEMBERSHIP = "membership";

  @Basic
  @NotEmpty()
  @Access(AccessType.FIELD)
  private Date applicationDate;

  @Basic
  @Access(AccessType.FIELD)
  private Date dateOfReply;

  @Basic
  @NotEmpty()
  @Enumerated(EnumType.STRING)
  @Access(AccessType.FIELD)
  private Status status;

  @ManyToOne(fetch = FetchType.LAZY)
  @NotEmpty()
  private Membership membership;


  public Date getApplicationDate() {
    return applicationDate;
  }

  public void setApplicationDate(final Date applicationDate) {
    this.applicationDate = applicationDate;
  }

  public Date getDateOfReply() {
    return dateOfReply;
  }

  public void setDateOfReply(final Date dateOfReply) {
    this.dateOfReply = dateOfReply;
  }

  public Status getStatus() {
    return status;
  }

  public void setStatus(final Status status) {
    this.status = status;
  }


  public Membership getMembership() {
    return membership;
  }

  public void setMembership(final Membership membership) {
    this.membership = membership;
  }

}