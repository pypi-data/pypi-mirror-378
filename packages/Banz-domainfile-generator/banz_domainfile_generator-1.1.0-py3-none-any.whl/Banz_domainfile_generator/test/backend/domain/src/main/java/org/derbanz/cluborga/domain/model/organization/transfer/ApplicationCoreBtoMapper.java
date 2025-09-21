// generated
package org.derbanz.cluborga.domain.model.organization.transfer;

import jakarta.inject.Inject;
import jakarta.persistence.EntityManager;
import org.derbanz.cluborga.domain.base.transfer.BaseBtoMapper;
import org.derbanz.cluborga.domain.model.organization.Application;

import java.util.Objects;

public class ApplicationCoreBtoMapper extends BaseBtoMapper {

  @Inject
  EntityManager entityManager;
  @Inject
  MembershipBtoMapper membershipBtoMapper;

  private boolean mapPropertiesToBo(ApplicationCoreBto bto, Application bo) {
    boolean result = checkIsNotEqual(bto, bo);

    if (!Objects.isNull(bto.getApplicationDate())) {
      bo.setApplicationDate(bto.getApplicationDate());
    }
    if (!Objects.isNull(bto.getDateOfReply())) {
      bo.setDateOfReply(bto.getDateOfReply());
    }
    if (!Objects.isNull(bto.getStatus())) {
      bo.setStatus(bto.getStatus());
    }
    return result;
  }

  private void mapPropertiesToBto(Application bo, ApplicationCoreBto bto) {
    mapBasePropertiesToBto(bo, bto);
    bto.setApplicationDate(bo.getApplicationDate());
    bto.setDateOfReply(bo.getDateOfReply());
    bto.setStatus(bo.getStatus());
  }

  public void mapToBto(Application bo, ApplicationBto bto) {
    mapPropertiesToBto(bo, bto);
    if (bo.getMembership() != null) {
      bto.setMembership(membershipBtoMapper.toBto(bo.getMembership()));
    }
  }

  public ApplicationBto toBto(Application bo) {
    ApplicationBto bto = new ApplicationBto();
    mapToBto(bo, bto);
    return bto;
  }

  public boolean mapToBo(Application bo, ApplicationBto bto) {
    if (bto.getMembership() != null) {
      bo.setMembership(membershipBtoMapper.toBo(bto.getMembership()));
    }
    return mapPropertiesToBo(bto, bo);
  }

  public Application toBo(ApplicationBto bto) {
    Application bo;
    if (bto.getId() != null) {
      bo = entityManager.find(Application.class, bto.getId());
    } else {
      bo = new Application();
    }
    mapToBo(bo, bto);
    return bo;
  }

  private boolean checkIsNotEqual(ApplicationCoreBto bto, Application bo) {
    return !Objects.equals(bo.getApplicationDate(), bto.getApplicationDate())
             || !Objects.equals(bo.getDateOfReply(), bto.getDateOfReply())
             || !Objects.equals(bo.getStatus(), bto.getStatus());
  }
}