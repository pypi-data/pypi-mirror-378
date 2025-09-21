// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import org.derbanz.cluborga.domain.base.transfer.BaseBtoMapper;
import org.derbanz.cluborga.domain.model.organization.Contact;

import java.util.Objects;

public class ContactCoreBtoMapper extends BaseBtoMapper {

  @Inject
  EntityManager entityManager;
  @Inject
  PersonBtoMapper personBtoMapper;

  private boolean mapPropertiesToBo(ContactCoreBto bto, Contact bo) {
    boolean result = checkIsNotEqual(bto, bo);

    if (!Objects.isNull(bto.getValidFrom())) {
      bo.setValidFrom(bto.getValidFrom());
    }
    if (!Objects.isNull(bto.getValidTo())) {
      bo.setValidTo(bto.getValidTo());
    }
    if (!Objects.isNull(bto.getType())) {
      bo.setType(bto.getType());
    }
    if (!Objects.isNull(bto.getStreet())) {
      bo.setStreet(bto.getStreet());
    }
    if (!Objects.isNull(bto.getNumber())) {
      bo.setNumber(bto.getNumber());
    }
    if (!Objects.isNull(bto.getNumberSuffix())) {
      bo.setNumberSuffix(bto.getNumberSuffix());
    }
    if (!Objects.isNull(bto.getPostbox())) {
      bo.setPostbox(bto.getPostbox());
    }
    if (!Objects.isNull(bto.getZip())) {
      bo.setZip(bto.getZip());
    }
    if (!Objects.isNull(bto.getCity())) {
      bo.setCity(bto.getCity());
    }
    if (!Objects.isNull(bto.getCountry())) {
      bo.setCountry(bto.getCountry());
    }
    if (!Objects.isNull(bto.getCountryCode())) {
      bo.setCountryCode(bto.getCountryCode());
    }
    if (!Objects.isNull(bto.getPhoneNumber())) {
      bo.setPhoneNumber(bto.getPhoneNumber());
    }
    if (!Objects.isNull(bto.getEmail())) {
      bo.setEmail(bto.getEmail());
    }
    return result;
  }

  private void mapPropertiesToBto(Contact bo, ContactCoreBto bto) {
    mapBasePropertiesToBto(bo, bto);
    bto.setValidFrom(bo.getValidFrom());
    bto.setValidTo(bo.getValidTo());
    bto.setType(bo.getType());
    bto.setStreet(bo.getStreet());
    bto.setNumber(bo.getNumber());
    bto.setNumberSuffix(bo.getNumberSuffix());
    bto.setPostbox(bo.getPostbox());
    bto.setZip(bo.getZip());
    bto.setCity(bo.getCity());
    bto.setCountry(bo.getCountry());
    bto.setCountryCode(bo.getCountryCode());
    bto.setPhoneNumber(bo.getPhoneNumber());
    bto.setEmail(bo.getEmail());
  }

  public void mapToBto(Contact bo, ContactBto bto) {
    mapPropertiesToBto(bo, bto);
    if (bo.getPerson() != null) {
      bto.setPerson(personBtoMapper.toBto(bo.getPerson()));
    }
  }

  public ContactBto toBto(Contact bo) {
    ContactBto bto = new ContactBto();
    mapToBto(bo, bto);
    return bto;
  }

  public boolean mapToBo(Contact bo, ContactBto bto) {
    if (bto.getPerson() != null) {
      bo.setPerson(personBtoMapper.toBo(bto.getPerson()));
    }
    return mapPropertiesToBo(bto, bo);
  }

  public Contact toBo(ContactBto bto) {
    Contact bo;
    if (bto.getId() != null) {
      bo = entityManager.find(Contact.class, bto.getId());
    } else {
      bo = new Contact();
    }
    mapToBo(bo, bto);
    return bo;
  }

  private boolean checkIsNotEqual(ContactCoreBto bto, Contact bo) {
    return !Objects.equals(bo.getValidFrom(), bto.getValidFrom())
             || !Objects.equals(bo.getValidTo(), bto.getValidTo())
             || !Objects.equals(bo.getType(), bto.getType())
             || !Objects.equals(bo.getStreet(), bto.getStreet())
             || !Objects.equals(bo.getNumber(), bto.getNumber())
             || !Objects.equals(bo.getNumberSuffix(), bto.getNumberSuffix())
             || !Objects.equals(bo.getPostbox(), bto.getPostbox())
             || !Objects.equals(bo.getZip(), bto.getZip())
             || !Objects.equals(bo.getCity(), bto.getCity())
             || !Objects.equals(bo.getCountry(), bto.getCountry())
             || !Objects.equals(bo.getCountryCode(), bto.getCountryCode())
             || !Objects.equals(bo.getPhoneNumber(), bto.getPhoneNumber())
             || !Objects.equals(bo.getEmail(), bto.getEmail());
  }
}