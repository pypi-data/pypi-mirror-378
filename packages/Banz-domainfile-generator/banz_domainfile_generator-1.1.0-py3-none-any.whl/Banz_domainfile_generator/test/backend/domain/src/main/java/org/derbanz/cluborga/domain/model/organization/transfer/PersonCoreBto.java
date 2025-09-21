// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.transfer.BaseBto;
import org.derbanz.cluborga.domain.enums.Gender;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Objects;

public class PersonCoreBto extends BaseBto {

  @NotEmpty
  private String name;

  private String firstName;

  private Date dateOfBirth;

  @NotNull
  private Gender gender;

  @Valid
  private List<MembershipBto> memberships;

  @Valid
  private List<ContactBto> contacts;


  public String getName() {
    return name;
  }

  public void setName(String name) {
    Objects.requireNonNull(name, "Name cannot be null.");
    this.name = name;
  }

  public String getFirstName() {
    return firstName;
  }

  public void setFirstName(String firstName) {
    this.firstName = firstName;
  }

  public Date getDateOfBirth() {
    return dateOfBirth;
  }

  public void setDateOfBirth(Date dateOfBirth) {
    this.dateOfBirth = dateOfBirth;
  }

  public Gender getGender() {
    return gender;
  }

  public void setGender(Gender gender) {
    Objects.requireNonNull(gender, "Gender cannot be null.");
    this.gender = gender;
  }

  public List<MembershipBto> getMemberships() {
    if (memberships == null) {
      setMemberships(new ArrayList<>());
    }
    return memberships;
  }

  public void setMemberships(List<MembershipBto> memberships) {
    this.memberships = memberships;
  }

  public List<ContactBto> getContacts() {
    if (contacts == null) {
      setContacts(new ArrayList<>());
    }
    return contacts;
  }

  public void setContacts(List<ContactBto> contacts) {
    this.contacts = contacts;
  }

}