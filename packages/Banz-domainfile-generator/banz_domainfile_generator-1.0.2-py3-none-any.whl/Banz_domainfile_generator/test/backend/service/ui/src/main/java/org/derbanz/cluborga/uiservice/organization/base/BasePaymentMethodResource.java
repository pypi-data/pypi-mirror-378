// generated
package org.derbanz.cluborga.uiservice.organization.base;

import jakarta.inject.Inject;
import jakarta.validation.ValidationException;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import org.derbanz.cluborga.commonservice.organization.PaymentMethodService;
import org.derbanz.cluborga.commonservice.organization.dto.PaymentMethodDto;

import java.util.List;

public class BasePaymentMethodResource {

  @Inject
  PaymentMethodService service;

  @POST
  @Path("validate")
  public void validate(PaymentMethodDto dto) throws ValidationException {
    service.validate(dto);
  }

  @POST
  @Path("save")
  public String save(PaymentMethodDto dto) throws ValidationException {
    return service.save(dto);
  }

  @GET
  @Path("get")
  @Consumes({MediaType.TEXT_PLAIN})
  public PaymentMethodDto get(@QueryParam("id") String id) {
    return service.get(id);
  }

  @GET
  @Path("getList")
  public List<PaymentMethodDto> getList(@QueryParam("ids") List<String> ids) {
    return service.getList(ids);
  }

  @GET
  @Path("getAll")
  public List<PaymentMethodDto> getAll() {
    return service.getAll();
  }

  @DELETE
  @Path("delete")
  public boolean delete(@QueryParam("id") String id) {
    return service.delete(id);
  }
}