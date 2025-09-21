// generated
package org.derbanz.cluborga.logic.organization.impl;

import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Root;
import jakarta.transaction.Transactional;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ValidationException;
import jakarta.validation.Validator;
import org.derbanz.cluborga.domain.base.exception.ObjectNotFoundException;
import org.derbanz.cluborga.domain.model.organization.Person;
import org.derbanz.cluborga.domain.model.organization.transfer.ContactBto;
import org.derbanz.cluborga.domain.model.organization.transfer.MembershipBto;
import org.derbanz.cluborga.domain.model.organization.transfer.PersonBto;
import org.derbanz.cluborga.domain.model.organization.transfer.PersonBtoMapper;
import org.derbanz.cluborga.logic.organization.BasePersonLogic;
import org.derbanz.cluborga.logic.organization.ContactLogic;
import org.derbanz.cluborga.logic.organization.MembershipLogic;
import org.jboss.logging.Logger;

import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class BasePersonLogicImpl implements BasePersonLogic {

  @Inject
  PersonBtoMapper btoMapper;
  @Inject
  EntityManager entityManager;
  @Inject
  Logger log;
  @Inject
  Validator validator;

  @Inject
  ContactLogic contactLogic;
  @Inject
  MembershipLogic membershipLogic;

  @Override
  public PersonBto instantiate() {
    PersonBto bto = new PersonBto();
    // override in logic to insert default parameters
    return bto;
  }

  @Override
  @Transactional
  public PersonBto get(String id) {
    Person bo = getBo(id);
    if (bo == null) {
      throw new ObjectNotFoundException(String.format("Person with id %s not found.", id));
    }
    return btoMapper.toBto(bo);
  }

  @Override
  @Transactional  public List<PersonBto> getList(List<String> ids) {
    List<UUID> idList = ids.stream().map(UUID::fromString).toList();
    CriteriaBuilder cb = entityManager.getCriteriaBuilder();
    CriteriaQuery<Person> query = cb.createQuery(Person.class);
    Root<Person> root = query.from(Person.class);
    query.where(root.get(Person.ID).in(idList));
    TypedQuery<Person> result = entityManager.createQuery(query);
    return result.getResultStream().map(btoMapper::toBto).toList();
  }

  @Override
  @Transactional  public List<PersonBto> getAll() {
    CriteriaBuilder cb = entityManager.getCriteriaBuilder();
    CriteriaQuery<Person> query = cb.createQuery(Person.class);
    Root<Person> root = query.from(Person.class);
    TypedQuery<Person> result = entityManager.createQuery(query);
    return result.getResultStream().map(btoMapper::toBto).toList();
  }

  @Override
  public Set<ConstraintViolation<PersonBto>> validate(PersonBto bto) {
    return validator.validate(bto);
  }

  @Override
  @Transactional
  public boolean save(PersonBto bto) {
    Set<? extends ConstraintViolation<?>> validationResult = validate(bto);
    if (!validationResult.isEmpty()) {
      String message = validationResult.stream()
                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage()))
                         .collect(Collectors.joining("\n"));
      throw new ValidationException(message);
    }
    if (bto.getId() == null || bto.getId().isEmpty()) {
      Person bo = new Person();
      btoMapper.mapToBo(bo, bto);
      entityManager.persist(bo);
      bto.setId(bo.getId().toString());
      bto.setCreation(bo.getCreation());
      bto.setCreationUser(bo.getCreationUser());
      bto.setLastUpdate(bo.getLastUpdate());
      bto.setLastUpdateUser(bo.getLastUpdateUser());
      handleConnectedObjects(bo, bto);
      log.info(String.format("%s created", bo));
      return true;
    } else {
      Person bo = getBo(bto.getId());
      boolean changes = btoMapper.mapToBo(bo, bto);
      handleConnectedObjects(bo, bto);
      if (changes) {
        entityManager.merge(bo);
        bto.setLastUpdate(bo.getLastUpdate());
        bto.setLastUpdateUser(bo.getLastUpdateUser());
        log.info(String.format("%s updated.", bo));
        return true;
      }
      return false;
    }
  }

  @Override  public boolean delete(PersonBto bto) {
    if (bto == null) {
      log.warn("Person not found for deletion.");
    }
    return delete(bto.getId());
  }

  @Override
  @Transactional
  public boolean delete(String id) {
    Person bo = getBo(id);
    if (bo != null) {
      entityManager.remove(bo);
      log.info(String.format("%s deleted.", bo));
      return true;
    } else {
      log.warn(String.format("Person with id %s not found for deletion.", id));
      return false;
    }
  }

  protected Person getBo(String id) {
    return entityManager.find(Person.class, UUID.fromString(id));
  }

  protected void handleConnectedObjects(Person bo, PersonBto bto) {
    handleMemberships(bo, bto);
    handleContacts(bo, bto);
  }

  private void handleMemberships(Person bo, PersonBto bto) {
    // Existing Bos without Bto are outdated and should be deleted
    List<String> membershipsInBto = bto.getMemberships().stream().map(MembershipBto::getId).toList();
    bo.getMemberships().stream().map(membershipBo -> membershipBo.getId().toString())
      .filter(membership -> !membershipsInBto.contains(membership))
      .forEach(membership -> membershipLogic.delete(membership));

    bto.getMemberships().forEach(membershipBto -> {
      if (membershipBto.getPerson() == null) {
        membershipBto.setPerson(bto);
      }
      membershipLogic.save(membershipBto);
    });
  }

  private void handleContacts(Person bo, PersonBto bto) {
    // Existing Bos without Bto are outdated and should be deleted
    List<String> contactsInBto = bto.getContacts().stream().map(ContactBto::getId).toList();
    bo.getContacts().stream().map(contactBo -> contactBo.getId().toString())
      .filter(contact -> !contactsInBto.contains(contact))
      .forEach(contact -> contactLogic.delete(contact));

    bto.getContacts().forEach(contactBto -> {
      if (contactBto.getPerson() == null) {
        contactBto.setPerson(bto);
      }
      contactLogic.save(contactBto);
    });
  }
}