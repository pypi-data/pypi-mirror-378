// generated
package org.derbanz.cluborga.domain.base;

import jakarta.persistence.*;
import org.hibernate.Hibernate;
import org.hibernate.annotations.UuidGenerator;

import java.io.Serializable;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

@MappedSuperclass
public class AbstractBusinessObject implements Serializable {

  public static final String ID = "id";
  public static final String VERSION = "version";
  public static final String CREATION = "creation";
  public static final String CREATION_USER = "creationUser";
  public static final String LAST_UPDATE = "lastUpdate";
  public static final String LAST_UPDATE_USER = "lastUpdateUser";

  @Id
  @GeneratedValue
  @UuidGenerator
  private UUID id;

  @Version
  private int version;

  @Basic
  private Timestamp creation;

  @Basic
  private String creationUser;

  @Basic
  private Timestamp lastUpdate;

  @Basic
  private String lastUpdateUser;

  public AbstractBusinessObject() {
  }

  @PrePersist
  protected void onCreate() {
    this.creation = Timestamp.from(Instant.now());
    this.lastUpdate = Timestamp.from(Instant.now());
    this.creationUser = getCurrentUsername();
    this.lastUpdateUser = getCurrentUsername();
  }

  @PreUpdate
  protected void onUpdate() {
    this.lastUpdate = Timestamp.from(Instant.now());
    this.lastUpdateUser = getCurrentUsername();
  }

  public UUID getId() {
    return this.id;
  }

  public void setId(UUID id) {
    this.id = id;
  }

  public int getVersion() {
    return this.version;
  }

  public void setVersion(int version) {
    this.version = version;
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

  @Override
  public boolean equals(Object object) {
    if (this == object) {
      return true;
    }
    if (object == null || !Hibernate.getClass(this).equals(Hibernate.getClass(object))) {
      return false;
    }
    AbstractBusinessObject other = (AbstractBusinessObject) object;
    return Objects.equals(this.getId(), other.getId());
  }

  private String getCurrentUsername() {
    return "system";
  }
}