// generated
package org.derbanz.cluborga.domain.base.dto;

import java.sql.Timestamp;

public class BaseDto {

  private String id;
  private Timestamp creation;
  private String creationUser;
  private Timestamp lastUpdate;
  private String lastUpdateUser;

  public String getId() {
    return this.id;
  }

  public void setId(String id) {
    this.id = id;
  }

  public Timestamp getCreation() {
    return this.creation;
  }

  public void setCreation(Timestamp creation) {
    this.creation = creation;
  }

  public String getCreationUser() {
    return this.creationUser;
  }

  public void setCreationUser(String creationUser) {
    this.creationUser = creationUser;
  }

  public Timestamp getLastUpdate() {
    return this.lastUpdate;
  }

  public void setLastUpdate(Timestamp lastUpdate) {
    this.lastUpdate = lastUpdate;
  }

  public String getLastUpdateUser() {
    return this.lastUpdateUser;
  }

  public void setLastUpdateUser(String lastUpdateUser) {
    this.lastUpdateUser = lastUpdateUser;
  }

}