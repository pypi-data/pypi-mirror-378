// generated
package org.derbanz.cluborga.domain.model.organization;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.AbstractBusinessObject;
import org.derbanz.cluborga.domain.enums.Gender;

import java.util.Date;
import java.util.HashSet;
import java.util.Set;

@Entity(
  name = "org.derbanz.cluborga.domain.model.organization.Person"
)
@Table(
  name = "co_person"
)
public class Person extends AbstractBusinessObject {

  public static final String NAME = "name";
  public static final String FIRST_NAME = "firstName";
  public static final String DATE_OF_BIRTH = "dateOfBirth";
  public static final String GENDER = "gender";

  public static final String MEMBERSHIPS = "memberships";
  public static final String CONTACTS = "contacts";

  @Basic
  @NotEmpty()
  @Access(AccessType.FIELD)
  private String name;

  @Basic
  @Access(AccessType.FIELD)
  private String firstName;

  @Basic
  @Access(AccessType.FIELD)
  private Date dateOfBirth;

  @Basic
  @NotEmpty()
  @Enumerated(EnumType.STRING)
  @Access(AccessType.FIELD)
  private Gender gender;

  @OneToMany(
    cascade = {
      CascadeType.REMOVE
    },
    fetch = FetchType.LAZY,
    orphanRemoval = true
  )
  private Set<Membership> memberships;

  @OneToMany(
    cascade = {
      CascadeType.REMOVE
    },
    fetch = FetchType.LAZY,
    orphanRemoval = true
  )
  private Set<Contact> contacts;


  public String getName() {
    return name;
  }

  public void setName(final String name) {
    this.name = name;
  }

  public String getFirstName() {
    return firstName;
  }

  public void setFirstName(final String firstName) {
    this.firstName = firstName;
  }

  public Date getDateOfBirth() {
    return dateOfBirth;
  }

  public void setDateOfBirth(final Date dateOfBirth) {
    this.dateOfBirth = dateOfBirth;
  }

  public Gender getGender() {
    return gender;
  }

  public void setGender(final Gender gender) {
    this.gender = gender;
  }


  public Set<Membership> getMemberships() {
    return memberships;
  }

  public void setMemberships(final Set<Membership> memberships) {
    this.memberships = memberships;
  }

  public boolean addSet<Membership>(final Set<Membership> membership) {
    if (membership == null) {
      return false;
    }
    membership.setPerson(this);
    if (!(this.memberships.contains(membership))) {
      return this.memberships.add(membership);
    }
    return false;
  }
  public Set<Contact> getContacts() {
    return contacts;
  }

  public void setContacts(final Set<Contact> contacts) {
    this.contacts = contacts;
  }

  public boolean addSet<Contact>(final Set<Contact> contact) {
    if (contact == null) {
      return false;
    }
    contact.setPerson(this);
    if (!(this.contacts.contains(contact))) {
      return this.contacts.add(contact);
    }
    return false;
  }
}