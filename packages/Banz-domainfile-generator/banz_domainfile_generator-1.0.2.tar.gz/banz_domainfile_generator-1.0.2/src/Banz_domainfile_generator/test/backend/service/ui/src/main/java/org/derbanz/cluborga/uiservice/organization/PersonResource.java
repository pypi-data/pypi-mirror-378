package org.derbanz.cluborga.uiservice.organization;

import jakarta.ws.rs.Consume;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.derbanz.cluborga.uiservice.organization.base.BasePersonResource;

@Path("/ui/organization")
@Produces({MediaType.APPLICATION_JSON})
@Consumes({MediaType.APPLICATION_JSON})
public class PersonResource extends BasePersonResource {
}