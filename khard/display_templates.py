from . import helpers

def print_standard_template(vcard, show_address_book=True, show_uid=True):
    """
    The standard no frills output
    """
    strings = []

    # name
    if vcard._get_first_names() or vcard._get_last_names():
        names = []
        if vcard._get_name_prefixes():
            names += vcard._get_name_prefixes()
        if vcard._get_first_names():
            names += vcard._get_first_names()
        if vcard._get_additional_names():
            names += vcard._get_additional_names()
        if vcard._get_last_names():
            names += vcard._get_last_names()
        if vcard._get_name_suffixes():
            names += vcard._get_name_suffixes()
        strings.append("Name: %s" % helpers.list_to_string(names, " "))
    # organisation
    if vcard._get_organisations():
        strings += helpers.convert_to_yaml(
            "Organisation", vcard._get_organisations(), 0, -1, False)
    # fn as fallback
    if not strings:
        strings.append("Name: %s" % vcard.get_full_name())

    # address book name
    if show_address_book:
        strings.append("Address book: %s" % vcard.address_book.name)

    # person related information
    if vcard.get_birthday() is not None or vcard.get_anniversary() is not None \
            or vcard.get_nicknames() or vcard._get_roles() or vcard._get_titles():
        strings.append("General:")
        if vcard.get_anniversary():
            strings.append("    Anniversary: %s"
                            % vcard.get_formatted_anniversary())
        if vcard.get_birthday():
            strings.append(
                "    Birthday: {}".format(vcard.get_formatted_birthday()))
        if vcard.get_nicknames():
            strings += helpers.convert_to_yaml(
                "Nickname", vcard.get_nicknames(), 4, -1, False)
        if vcard._get_roles():
            strings += helpers.convert_to_yaml(
                "Role", vcard._get_roles(), 4, -1, False)
        if vcard._get_titles():
            strings += helpers.convert_to_yaml(
                "Title", vcard._get_titles(), 4, -1, False)

    # phone numbers
    if vcard.get_phone_numbers().keys():
        strings.append("Phone")
        for type, number_list in sorted(
                vcard.get_phone_numbers().items(),
                key=lambda k: k[0].lower()):
            strings += helpers.convert_to_yaml(
                type, number_list, 4, -1, False)

    # email addresses
    if vcard.get_email_addresses().keys():
        strings.append("E-Mail")
        for type, email_list in sorted(
                vcard.get_email_addresses().items(),
                key=lambda k: k[0].lower()):
            strings += helpers.convert_to_yaml(
                type, email_list, 4, -1, False)

    # post addresses
    if vcard._get_post_addresses().keys():
        strings.append("Address")
        for type, post_adr_list in sorted(
                vcard._get_formatted_post_addresses().items(),
                key=lambda k: k[0].lower()):
            strings += helpers.convert_to_yaml(
                type, post_adr_list, 4, -1, False)

    # private objects
    if vcard._get_private_objects().keys():
        strings.append("Private:")
        for object in vcard.supported_private_objects:
            if object in vcard._get_private_objects():
                strings += helpers.convert_to_yaml(
                    object, vcard._get_private_objects().get(object), 4, -1,
                    False)

    # misc stuff
    if vcard._get_categories() or (show_uid and vcard.get_uid() != "") \
            or vcard._get_webpages() or vcard._get_notes():
        strings.append("Miscellaneous")
        if show_uid and vcard.get_uid():
            strings.append("    UID: {}".format(vcard.get_uid()))
        if vcard._get_categories():
            strings += helpers.convert_to_yaml(
                "Categories", vcard._get_categories(), 4, -1, False)
        if vcard._get_webpages():
            strings += helpers.convert_to_yaml(
                "Webpage", vcard._get_webpages(), 4, -1, False)
        if vcard._get_notes():
            strings += helpers.convert_to_yaml(
                "Note", vcard._get_notes(), 4, -1, False)
    return '\n'.join(strings)


def print_rolodex_template(vcard, **kwargs):
    pass
