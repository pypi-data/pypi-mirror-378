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
import org.derbanz.cluborga.domain.model.organization.PaymentMethod;
import org.derbanz.cluborga.domain.model.organization.transfer.PaymentMethodBto;
import org.derbanz.cluborga.domain.model.organization.transfer.PaymentMethodBtoMapper;
import org.derbanz.cluborga.logic.organization.BasePaymentMethodLogic;
import org.jboss.logging.Logger;

import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class BasePaymentMethodLogicImpl implements BasePaymentMethodLogic {

  @Inject
  PaymentMethodBtoMapper btoMapper;
  @Inject
  EntityManager entityManager;
  @Inject
  Logger log;
  @Inject
  Validator validator;

  @Override
  public PaymentMethodBto instantiate() {
    PaymentMethodBto bto = new PaymentMethodBto();
    // override in logic to insert default parameters
    return bto;
  }

  @Override
  @Transactional
  public PaymentMethodBto get(String id) {
    PaymentMethod bo = getBo(id);
    if (bo == null) {
      throw new ObjectNotFoundException(String.format("PaymentMethod with id %s not found.", id));
    }
    return btoMapper.toBto(bo);
  }

  @Override
  @Transactional  public List<PaymentMethodBto> getList(List<String> ids) {
    List<UUID> idList = ids.stream().map(UUID::fromString).toList();
    CriteriaBuilder cb = entityManager.getCriteriaBuilder();
    CriteriaQuery<PaymentMethod> query = cb.createQuery(PaymentMethod.class);
    Root<PaymentMethod> root = query.from(PaymentMethod.class);
    query.where(root.get(PaymentMethod.ID).in(idList));
    TypedQuery<PaymentMethod> result = entityManager.createQuery(query);
    return result.getResultStream().map(btoMapper::toBto).toList();
  }

  @Override
  @Transactional  public List<PaymentMethodBto> getAll() {
    CriteriaBuilder cb = entityManager.getCriteriaBuilder();
    CriteriaQuery<PaymentMethod> query = cb.createQuery(PaymentMethod.class);
    Root<PaymentMethod> root = query.from(PaymentMethod.class);
    TypedQuery<PaymentMethod> result = entityManager.createQuery(query);
    return result.getResultStream().map(btoMapper::toBto).toList();
  }

  @Override
  public Set<ConstraintViolation<PaymentMethodBto>> validate(PaymentMethodBto bto) {
    return validator.validate(bto);
  }

  @Override
  @Transactional
  public boolean save(PaymentMethodBto bto) {
    Set<? extends ConstraintViolation<?>> validationResult = validate(bto);
    if (!validationResult.isEmpty()) {
      String message = validationResult.stream()
                         .map(val -> String.valueOf(val.getPropertyPath()).concat(": ").concat(val.getMessage()))
                         .collect(Collectors.joining("\n"));
      throw new ValidationException(message);
    }
    if (bto.getId() == null || bto.getId().isEmpty()) {
      PaymentMethod bo = new PaymentMethod();
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
      PaymentMethod bo = getBo(bto.getId());
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

  @Override  public boolean delete(PaymentMethodBto bto) {
    if (bto == null) {
      log.warn("Person not found for deletion.");
    }
    return delete(bto.getId());
  }

  @Override
  @Transactional
  public boolean delete(String id) {
    PaymentMethod bo = getBo(id);
    if (bo != null) {
      entityManager.remove(bo);
      log.info(String.format("%s deleted.", bo));
      return true;
    } else {
      log.warn(String.format("PaymentMethod with id %s not found for deletion.", id));
      return false;
    }
  }

  protected PaymentMethod getBo(String id) {
    return entityManager.find(PaymentMethod.class, UUID.fromString(id));
  }

  protected void handleConnectedObjects(PaymentMethod bo, PaymentMethodBto bto) {
  }
}