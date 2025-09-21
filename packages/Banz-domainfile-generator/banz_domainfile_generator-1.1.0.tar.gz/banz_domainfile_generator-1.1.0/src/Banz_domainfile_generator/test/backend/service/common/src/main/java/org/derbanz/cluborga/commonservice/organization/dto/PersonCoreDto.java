// generated
package org.derbanz.cluborga.commonservice.organization.dto;

import org.derbanz.cluborga.domain.base.dto.BaseDto;
import org.derbanz.cluborga.domain.enums.Gender;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;

public class PersonCoreDto extends BaseDto {

  private String name;
  private String firstName;
  private Date dateOfBirth;
  private Gender gender;

  private List<MembershipDto> memberships;
  private List<ContactDto> contacts;

  public String getName() {
    return name;
  }

  public void setName(String name) {
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
    this.gender = gender;
  }

  public List<MembershipDto> getMemberships() {
    if (memberships == null) {
      setMemberships(new ArrayList<>());
    }
    return memberships;
  }

  public void setMemberships(List<MembershipDto> memberships) {
    this.memberships = memberships;
  }

  public List<ContactDto> getContacts() {
    if (contacts == null) {
      setContacts(new ArrayList<>());
    }
    return contacts;
  }

  public void setContacts(List<ContactDto> contacts) {
    this.contacts = contacts;
  }

}