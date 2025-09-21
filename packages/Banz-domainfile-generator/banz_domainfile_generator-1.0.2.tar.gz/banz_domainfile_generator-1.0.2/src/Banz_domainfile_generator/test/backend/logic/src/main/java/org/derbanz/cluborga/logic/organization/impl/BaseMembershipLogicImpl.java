// generated
package org.derbanz.cluborga.logic.organization.impl;

import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Root;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.ValidationException;
import jakarta.validation.Validator;
import org.derbanz.cluborga.domain.base.exception.ObjectNotFoundException;
import org.derbanz.cluborga.domain.model.organization.Membership;
import org.derbanz.cluborga.domain.model.organization.transfer.MembershipBto;
import org.derbanz.cluborga.domain.model.organization.transfer.MembershipBtoMapper;
import org.derbanz.cluborga.logic.organization.BaseMembershipLogic;
import org.jboss.logging.Logger;

import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class BaseMembershipLogicImpl implements BaseMembershipLogic {

  @Inject
  MembershipBtoMapper btoMapper;
  @Inject
  EntityManager entityManager;
  @Inject
  Logger log;
  @Inject
  Validator validator;

  @Override
  public MembershipBto instantiate() {
    MembershipBto bto = new MembershipBto();
    // override in logic to insert default parameters
    return bto;
  }

  @Override
  @Transactional
  public MembershipBto get(String id) {
    Membership bo = getBo(id);
    if (bo == null) {
      throw new ObjectNotFoundException(String.format("Membership with id %s not found.", id));
    }
    return btoMapper.toBto(bo);
  }

  @Override
  @Transactional  public List<MembershipBto> getList(List<String> ids) {
    List<UUID> idList = ids.stream().map(UUID::fromString).toList();
    CriteriaBuilder cb = entityManager.getCriteriaBuilder();
    CriteriaQuery<Membership> query = cb.createQuery(Membership.class);
    Root<Membership> root = query.from(Membership.class);
    query.where(root.get(Membership.ID).in(idList));
    TypedQuery<Membership> result = entityManager.createQuery(query);
    return result.getResultStream().map(btoMapper::toBto).toList();
  }

  @Override
  @Transactional  public List<MembershipBto> getAll() {
    CriteriaBuilder cb = entityManager.getCriteriaBuilder();
    CriteriaQuery<Membership> query = cb.createQuery(Membership.class);
    Root<Membership> root = query.from(Membership.class);
    TypedQuery<Membership> result = entityManager.createQuery(query);
    return result.getResultStream().map(btoMapper::toBto).toList();
  }

  @Override
  public Set<ConstraintViolation<MembershipBto>> validate(MembershipBto bto) {
    return validator.validate(bto);
  }

  @Override
  @Transactional
  public boolean save(MembershipBto bto) {
    Set<? extends ConstraintViolation<?>> validationResult = validate(bto);
    if (!validationResult.isEmpty()) {
      String message = validationResult.stream()
                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage()))
                         .collect(Collectors.joining("\n"));
      throw new ValidationException(message);
    }
    if (bto.getId() == null || bto.getId().isEmpty()) {
      Membership bo = new Membership();
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
      Membership bo = getBo(bto.getId());
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

  @Override  public boolean delete(MembershipBto bto) {
    if (bto == null) {
      log.warn("Person not found for deletion.");
    }
    return delete(bto.getId());
  }

  @Override
  @Transactional
  public boolean delete(String id) {
    Membership bo = getBo(id);
    if (bo != null) {
      entityManager.remove(bo);
      log.info(String.format("%s deleted.", bo));
      return true;
    } else {
      log.warn(String.format("Membership with id %s not found for deletion.", id));
      return false;
    }
  }

  protected Membership getBo(String id) {
    return entityManager.find(Membership.class, UUID.fromString(id));
  }

  protected void handleConnectedObjects(Membership bo, MembershipBto bto) {
  }
}