// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import org.derbanz.cluborga.domain.base.transfer.BaseBtoMapper;
import org.derbanz.cluborga.domain.model.organization.Membership;

import java.util.Objects;

public class MembershipCoreBtoMapper extends BaseBtoMapper {

  @Inject
  EntityManager entityManager;
  @Inject
  PersonBtoMapper personBtoMapper;

  private boolean mapPropertiesToBo(MembershipCoreBto bto, Membership bo) {
    boolean result = checkIsNotEqual(bto, bo);

    if (!Objects.isNull(bto.getValidFrom())) {
      bo.setValidFrom(bto.getValidFrom());
    }
    if (!Objects.isNull(bto.getValidTo())) {
      bo.setValidTo(bto.getValidTo());
    }
    if (!Objects.isNull(bto.getDiscount())) {
      bo.setDiscount(bto.getDiscount());
    }
    if (!Objects.isNull(bto.getStatus())) {
      bo.setStatus(bto.getStatus());
    }
    return result;
  }

  private void mapPropertiesToBto(Membership bo, MembershipCoreBto bto) {
    mapBasePropertiesToBto(bo, bto);
    bto.setValidFrom(bo.getValidFrom());
    bto.setValidTo(bo.getValidTo());
    bto.setDiscount(bo.getDiscount());
    bto.setStatus(bo.getStatus());
  }

  public void mapToBto(Membership bo, MembershipBto bto) {
    mapPropertiesToBto(bo, bto);
    if (bo.getPerson() != null) {
      bto.setPerson(personBtoMapper.toBto(bo.getPerson()));
    }
  }

  public MembershipBto toBto(Membership bo) {
    MembershipBto bto = new MembershipBto();
    mapToBto(bo, bto);
    return bto;
  }

  public boolean mapToBo(Membership bo, MembershipBto bto) {
    if (bto.getPerson() != null) {
      bo.setPerson(personBtoMapper.toBo(bto.getPerson()));
    }
    return mapPropertiesToBo(bto, bo);
  }

  public Membership toBo(MembershipBto bto) {
    Membership bo;
    if (bto.getId() != null) {
      bo = entityManager.find(Membership.class, bto.getId());
    } else {
      bo = new Membership();
    }
    mapToBo(bo, bto);
    return bo;
  }

  private boolean checkIsNotEqual(MembershipCoreBto bto, Membership bo) {
    return !Objects.equals(bo.getValidFrom(), bto.getValidFrom())
             || !Objects.equals(bo.getValidTo(), bto.getValidTo())
             || !Objects.equals(bo.getDiscount(), bto.getDiscount())
             || !Objects.equals(bo.getStatus(), bto.getStatus());
  }
}