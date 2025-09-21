// generated
package org.derbanz.cluborga.domain.base;

import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.core.Context;
import jakarta.ws.rs.core.HttpHeaders;

import java.util.Locale;
import java.util.ResourceBundle;

@ApplicationScoped
public class I18N {

  @Context
  HttpHeaders headers;

  public String getLocalizedValue(String key) {
    Locale locale = getCurrentLocale();
    ResourceBundle bundle = ResourceBundle.getBundle("constants.i18n", locale);
    return bundle.getString(key);
  }

  private Locale getCurrentLocale() {
    Locale locale = Locale.getDefault();
    if (headers != null && !headers.getAcceptableLanguages().isEmpty()) {
      locale = headers.getAcceptableLanguages().getFirst();
    }
    return locale;
  }
}