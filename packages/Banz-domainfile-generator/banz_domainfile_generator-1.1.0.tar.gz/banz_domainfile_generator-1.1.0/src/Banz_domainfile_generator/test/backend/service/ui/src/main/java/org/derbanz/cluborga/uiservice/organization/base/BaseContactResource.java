// generated
package org.derbanz.cluborga.uiservice.organization.base;

import jakarta.inject.Inject;
import jakarta.validation.ValidationException;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import org.derbanz.cluborga.commonservice.organization.ContactService;
import org.derbanz.cluborga.commonservice.organization.dto.ContactDto;

import java.util.List;

public class BaseContactResource {

  @Inject
  ContactService service;

  @POST
  @Path("validate")
  public void validate(ContactDto dto) throws ValidationException {
    service.validate(dto);
  }

  @POST
  @Path("save")
  public String save(ContactDto dto) throws ValidationException {
    return service.save(dto);
  }

  @GET
  @Path("get")
  @Consumes({MediaType.TEXT_PLAIN})
  public ContactDto get(@QueryParam("id") String id) {
    return service.get(id);
  }

  @GET
  @Path("getList")
  public List<ContactDto> getList(@QueryParam("ids") List<String> ids) {
    return service.getList(ids);
  }

  @GET
  @Path("getAll")
  public List<ContactDto> getAll() {
    return service.getAll();
  }

  @DELETE
  @Path("delete")
  public boolean delete(@QueryParam("id") String id) {
    return service.delete(id);
  }
}