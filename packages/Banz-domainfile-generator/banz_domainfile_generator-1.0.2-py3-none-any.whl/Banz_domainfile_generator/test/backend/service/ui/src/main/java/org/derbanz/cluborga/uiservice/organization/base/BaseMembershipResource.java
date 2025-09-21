// generated
package org.derbanz.cluborga.uiservice.organization.base;

import jakarta.inject.Inject;
import jakarta.validation.ValidationException;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import org.derbanz.cluborga.commonservice.organization.MembershipService;
import org.derbanz.cluborga.commonservice.organization.dto.MembershipDto;

import java.util.List;

public class BaseMembershipResource {

  @Inject
  MembershipService service;

  @POST
  @Path("validate")
  public void validate(MembershipDto dto) throws ValidationException {
    service.validate(dto);
  }

  @POST
  @Path("save")
  public String save(MembershipDto dto) throws ValidationException {
    return service.save(dto);
  }

  @GET
  @Path("get")
  @Consumes({MediaType.TEXT_PLAIN})
  public MembershipDto get(@QueryParam("id") String id) {
    return service.get(id);
  }

  @GET
  @Path("getList")
  public List<MembershipDto> getList(@QueryParam("ids") List<String> ids) {
    return service.getList(ids);
  }

  @GET
  @Path("getAll")
  public List<MembershipDto> getAll() {
    return service.getAll();
  }

  @DELETE
  @Path("delete")
  public boolean delete(@QueryParam("id") String id) {
    return service.delete(id);
  }
}