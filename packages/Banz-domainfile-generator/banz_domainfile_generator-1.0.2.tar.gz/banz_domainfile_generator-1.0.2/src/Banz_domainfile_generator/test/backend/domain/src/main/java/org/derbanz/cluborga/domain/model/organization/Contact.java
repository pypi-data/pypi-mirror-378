// generated
package org.derbanz.cluborga.domain.model.organization;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.AbstractBusinessObject;
import org.derbanz.cluborga.domain.enums.ContactType;

import java.util.Date;

@Entity(
  name = "org.derbanz.cluborga.domain.model.organization.Contact"
)
@Table(
  name = "co_contact"
)
public class Contact extends AbstractBusinessObject {

  public static final String VALID_FROM = "validFrom";
  public static final String VALID_TO = "validTo";
  public static final String TYPE = "type";
  public static final String STREET = "street";
  public static final String NUMBER = "number";
  public static final String NUMBER_SUFFIX = "numberSuffix";
  public static final String POSTBOX = "postbox";
  public static final String ZIP = "zip";
  public static final String CITY = "city";
  public static final String COUNTRY = "country";
  public static final String COUNTRY_CODE = "countryCode";
  public static final String PHONE_NUMBER = "phoneNumber";
  public static final String EMAIL = "email";

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
  @Enumerated(EnumType.STRING)
  @Access(AccessType.FIELD)
  private ContactType type;

  @Basic
  @Access(AccessType.FIELD)
  private String street;

  @Basic
  @Access(AccessType.FIELD)
  private String number;

  @Basic
  @Access(AccessType.FIELD)
  private String numberSuffix;

  @Basic
  @Access(AccessType.FIELD)
  private String postbox;

  @Basic
  @Access(AccessType.FIELD)
  private String zip;

  @Basic
  @Access(AccessType.FIELD)
  private String city;

  @Basic
  @Access(AccessType.FIELD)
  private String country;

  @Basic
  @Access(AccessType.FIELD)
  private String countryCode;

  @Basic
  @Access(AccessType.FIELD)
  private String phoneNumber;

  @Basic
  @Access(AccessType.FIELD)
  private String email;

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

  public ContactType getType() {
    return type;
  }

  public void setType(final ContactType type) {
    this.type = type;
  }

  public String getStreet() {
    return street;
  }

  public void setStreet(final String street) {
    this.street = street;
  }

  public String getNumber() {
    return number;
  }

  public void setNumber(final String number) {
    this.number = number;
  }

  public String getNumberSuffix() {
    return numberSuffix;
  }

  public void setNumberSuffix(final String numberSuffix) {
    this.numberSuffix = numberSuffix;
  }

  public String getPostbox() {
    return postbox;
  }

  public void setPostbox(final String postbox) {
    this.postbox = postbox;
  }

  public String getZip() {
    return zip;
  }

  public void setZip(final String zip) {
    this.zip = zip;
  }

  public String getCity() {
    return city;
  }

  public void setCity(final String city) {
    this.city = city;
  }

  public String getCountry() {
    return country;
  }

  public void setCountry(final String country) {
    this.country = country;
  }

  public String getCountryCode() {
    return countryCode;
  }

  public void setCountryCode(final String countryCode) {
    this.countryCode = countryCode;
  }

  public String getPhoneNumber() {
    return phoneNumber;
  }

  public void setPhoneNumber(final String phoneNumber) {
    this.phoneNumber = phoneNumber;
  }

  public String getEmail() {
    return email;
  }

  public void setEmail(final String email) {
    this.email = email;
  }


  public Person getPerson() {
    return person;
  }

  public void setPerson(final Person person) {
    this.person = person;
  }

}