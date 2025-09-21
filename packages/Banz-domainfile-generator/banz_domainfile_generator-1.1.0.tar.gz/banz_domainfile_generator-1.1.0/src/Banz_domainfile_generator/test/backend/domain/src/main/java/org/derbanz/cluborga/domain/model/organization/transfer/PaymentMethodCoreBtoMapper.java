// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import org.derbanz.cluborga.domain.base.transfer.BaseBtoMapper;
import org.derbanz.cluborga.domain.model.organization.PaymentMethod;

import java.util.Objects;

public class PaymentMethodCoreBtoMapper extends BaseBtoMapper {

  @Inject
  EntityManager entityManager;
  @Inject
  MembershipBtoMapper membershipBtoMapper;

  private boolean mapPropertiesToBo(PaymentMethodCoreBto bto, PaymentMethod bo) {
    boolean result = checkIsNotEqual(bto, bo);

    if (!Objects.isNull(bto.getValidFrom())) {
      bo.setValidFrom(bto.getValidFrom());
    }
    if (!Objects.isNull(bto.getValidTo())) {
      bo.setValidTo(bto.getValidTo());
    }
    if (!Objects.isNull(bto.getIban())) {
      bo.setIban(bto.getIban());
    }
    if (!Objects.isNull(bto.getBic())) {
      bo.setBic(bto.getBic());
    }
    if (!Objects.isNull(bto.getBank())) {
      bo.setBank(bto.getBank());
    }
    if (!Objects.isNull(bto.getSepaMandate())) {
      bo.setSepaMandate(bto.getSepaMandate());
    }
    return result;
  }

  private void mapPropertiesToBto(PaymentMethod bo, PaymentMethodCoreBto bto) {
    mapBasePropertiesToBto(bo, bto);
    bto.setValidFrom(bo.getValidFrom());
    bto.setValidTo(bo.getValidTo());
    bto.setIban(bo.getIban());
    bto.setBic(bo.getBic());
    bto.setBank(bo.getBank());
    bto.setSepaMandate(bo.getSepaMandate());
  }

  public void mapToBto(PaymentMethod bo, PaymentMethodBto bto) {
    mapPropertiesToBto(bo, bto);
    if (bo.getMembership() != null) {
      bto.setMembership(membershipBtoMapper.toBto(bo.getMembership()));
    }
  }

  public PaymentMethodBto toBto(PaymentMethod bo) {
    PaymentMethodBto bto = new PaymentMethodBto();
    mapToBto(bo, bto);
    return bto;
  }

  public boolean mapToBo(PaymentMethod bo, PaymentMethodBto bto) {
    if (bto.getMembership() != null) {
      bo.setMembership(membershipBtoMapper.toBo(bto.getMembership()));
    }
    return mapPropertiesToBo(bto, bo);
  }

  public PaymentMethod toBo(PaymentMethodBto bto) {
    PaymentMethod bo;
    if (bto.getId() != null) {
      bo = entityManager.find(PaymentMethod.class, bto.getId());
    } else {
      bo = new PaymentMethod();
    }
    mapToBo(bo, bto);
    return bo;
  }

  private boolean checkIsNotEqual(PaymentMethodCoreBto bto, PaymentMethod bo) {
    return !Objects.equals(bo.getValidFrom(), bto.getValidFrom())
             || !Objects.equals(bo.getValidTo(), bto.getValidTo())
             || !Objects.equals(bo.getIban(), bto.getIban())
             || !Objects.equals(bo.getBic(), bto.getBic())
             || !Objects.equals(bo.getBank(), bto.getBank())
             || !Objects.equals(bo.getSepaMandate(), bto.getSepaMandate());
  }
}