// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import org.derbanz.cluborga.domain.base.transfer.BaseBto;
import org.derbanz.cluborga.domain.enums.ContactType;

import java.util.Date;
import java.util.Objects;

public class ContactCoreBto extends BaseBto {

  @NotEmpty
  private Date validFrom;

  private Date validTo;

  @NotNull
  private ContactType type;

  private String street;

  private String number;

  private String numberSuffix;

  private String postbox;

  private String zip;

  private String city;

  private String country;

  private String countryCode;

  private String phoneNumber;

  private String email;

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

  public ContactType getType() {
    return type;
  }

  public void setType(ContactType type) {
    Objects.requireNonNull(type, "Type cannot be null.");
    this.type = type;
  }

  public String getStreet() {
    return street;
  }

  public void setStreet(String street) {
    this.street = street;
  }

  public String getNumber() {
    return number;
  }

  public void setNumber(String number) {
    this.number = number;
  }

  public String getNumberSuffix() {
    return numberSuffix;
  }

  public void setNumberSuffix(String numberSuffix) {
    this.numberSuffix = numberSuffix;
  }

  public String getPostbox() {
    return postbox;
  }

  public void setPostbox(String postbox) {
    this.postbox = postbox;
  }

  public String getZip() {
    return zip;
  }

  public void setZip(String zip) {
    this.zip = zip;
  }

  public String getCity() {
    return city;
  }

  public void setCity(String city) {
    this.city = city;
  }

  public String getCountry() {
    return country;
  }

  public void setCountry(String country) {
    this.country = country;
  }

  public String getCountryCode() {
    return countryCode;
  }

  public void setCountryCode(String countryCode) {
    this.countryCode = countryCode;
  }

  public String getPhoneNumber() {
    return phoneNumber;
  }

  public void setPhoneNumber(String phoneNumber) {
    this.phoneNumber = phoneNumber;
  }

  public String getEmail() {
    return email;
  }

  public void setEmail(String email) {
    this.email = email;
  }


  public PersonBto getPerson() {
    return person;
  }

  public void setPerson(PersonBto person) {
    Objects.requireNonNull(person, "Person cannot be null.");
    this.person = person;
  }

}