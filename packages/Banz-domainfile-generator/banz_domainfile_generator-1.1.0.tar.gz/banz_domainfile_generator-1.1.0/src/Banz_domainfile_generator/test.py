from Banz_domainfile_generator.domainfile_generator import run

csv = 'organization;Application;applicationDate,DATE,required;dateOfReply,DATE;status,ENUM(Status/APPLICATION/ACCEPTED/DECLINED),required;membership,REFERENCE(organization.Membership/1),required'
csv += '\norganization;Contact;validFrom,DATE,required;validTo,DATE;type,ENUM(ContactType/ADDRESS/PHONE/EMAIL),required;street,STRING;number,STRING;numberSuffix,STRING;postbox,STRING;zip,STRING;city,STRING;country,STRING;countryCode,STRING;phoneNumber,STRING;email,STRING;person,REFERENCE(organization.Person/1),required'
csv += '\norganization;Membership;validFrom,DATE,required;validTo,DATE;discount,BOOLEAN,required;status,ENUM(MembershipStatus/APPLICATION/ACTIVE_MEMBER/INACTIVE_MEMBER/FORMER_MEMBER/DECLINED),required;person,REFERENCE(organization.Person/1),required'
csv += '\norganization;PaymentMethod;validFrom,DATE,required;validTo,DATE;iban,STRING,required;bic,STRING;bank,STRING;sepaMandate,BOOLEAN,required;membership,REFERENCE(organization.Membership/1),required'
csv += '\norganization;Person;name,STRING,required;firstName,STRING;dateOfBirth,DATE;gender,ENUM(Gender/MALE/FEMALE/DIVERSE),required;memberships,INCOMING_REFERENCE(organization.Membership/n);contacts,INCOMING_REFERENCE(organization.Contact/n)'

paths = {
    'domain': '\\test\\backend\\domain\\src\\main\\java\\org\\derbanz\\cluborga\\domain\\',
    'schema': '\\test\\backend\\domain\\src\\main\\resources\\schema\\',
    'logic': '\\test\\backend\\logic\\src\\main\\java\\org\\derbanz\\cluborga\\logic\\',
    'commonService': '\\test\\backend\\service\\common\\src\\main\\java\\org\\derbanz\\cluborga\\commonservice\\',
    'uiService': '\\test\\backend\\service\\ui\\src\\main\\java\\org\\derbanz\\cluborga\\uiservice\\'
}
    

run(csv, paths)