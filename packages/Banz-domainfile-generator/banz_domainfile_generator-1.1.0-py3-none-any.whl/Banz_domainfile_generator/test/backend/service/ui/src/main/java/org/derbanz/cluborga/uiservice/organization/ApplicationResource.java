package org.derbanz.cluborga.uiservice.organization;

import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.derbanz.cluborga.uiservice.organization.base.BaseApplicationResource;

@Path("/ui/organization/application")
@Produces({MediaType.APPLICATION_JSON})
@Consumes({MediaType.APPLICATION_JSON})
public class ApplicationResource extends BaseApplicationResource {
}