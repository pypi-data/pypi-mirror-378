// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import org.derbanz.cluborga.domain.base.transfer.BaseBtoMapper;
import org.derbanz.cluborga.domain.model.organization.Person;

import java.util.List;
import java.util.Objects;

public class PersonCoreBtoMapper extends BaseBtoMapper {

  @Inject
  EntityManager entityManager;
  @Inject
  ContactBtoMapper contactBtoMapper;
  @Inject
  MembershipBtoMapper membershipBtoMapper;

  private boolean mapPropertiesToBo(PersonCoreBto bto, Person bo) {
    boolean result = checkIsNotEqual(bto, bo);

    if (!Objects.isNull(bto.getName())) {
      bo.setName(bto.getName());
    }
    if (!Objects.isNull(bto.getFirstName())) {
      bo.setFirstName(bto.getFirstName());
    }
    if (!Objects.isNull(bto.getDateOfBirth())) {
      bo.setDateOfBirth(bto.getDateOfBirth());
    }
    if (!Objects.isNull(bto.getGender())) {
      bo.setGender(bto.getGender());
    }
    return result;
  }

  private void mapPropertiesToBto(Person bo, PersonCoreBto bto) {
    mapBasePropertiesToBto(bo, bto);
    bto.setName(bo.getName());
    bto.setFirstName(bo.getFirstName());
    bto.setDateOfBirth(bo.getDateOfBirth());
    bto.setGender(bo.getGender());
  }

  public void mapToBto(Person bo, PersonBto bto) {
    mapPropertiesToBto(bo, bto);
    bto.setMemberships(bo.getMemberships().stream().map(membershipBtoMapper::toBto).toList());
    bto.setContacts(bo.getContacts().stream().map(contactBtoMapper::toBto).toList());
  }

  public PersonBto toBto(Person bo) {
    PersonBto bto = new PersonBto();
    mapToBto(bo, bto);
    return bto;
  }

  public boolean mapToBo(Person bo, PersonBto bto) {
    bo.setMemberships(bto.getMemberships().stream().map(membershipBtoMapper::toBo).collect(Collectors.toSet()));
    bo.setContacts(bto.getContacts().stream().map(contactBtoMapper::toBo).collect(Collectors.toSet()));
    return mapPropertiesToBo(bto, bo);
  }

  public Person toBo(PersonBto bto) {
    Person bo;
    if (bto.getId() != null) {
      bo = entityManager.find(Person.class, bto.getId());
    } else {
      bo = new Person();
    }
    mapToBo(bo, bto);
    return bo;
  }

  private boolean checkIsNotEqual(PersonCoreBto bto, Person bo) {
    return !Objects.equals(bo.getName(), bto.getName())
             || !Objects.equals(bo.getFirstName(), bto.getFirstName())
             || !Objects.equals(bo.getDateOfBirth(), bto.getDateOfBirth())
             || !Objects.equals(bo.getGender(), bto.getGender());
  }
}