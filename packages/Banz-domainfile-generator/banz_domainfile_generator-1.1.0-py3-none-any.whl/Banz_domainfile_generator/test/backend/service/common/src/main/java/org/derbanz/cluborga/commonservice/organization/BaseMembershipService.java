// generated
package org.derbanz.cluborga.commonservice.organization;

import jakarta.validation.ValidationException;
import org.derbanz.cluborga.commonservice.organization.dto.MembershipDto;

import java.util.List;

public interface BaseMembershipService {

  void validate(MembershipDto dto) throws ValidationException;

  String save(MembershipDto dto) throws ValidationException;

  MembershipDto get(String id);

  List<MembershipDto> getList(List<String> ids);

  List<MembershipDto> getAll();

  boolean delete(String id);
}