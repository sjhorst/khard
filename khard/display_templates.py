from . import helpers
import re

class color:
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    CYAN = '\033[96m'

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
                type, '\n'.join(post_adr_list), 4, -1, False)

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
    import os
    from .config import Config
    from itertools import zip_longest

    config = Config()
    console_size = os.popen('stty size', 'r').read().split()
    console_width = min(80, int(console_size[1]))
    ellip = u'\u2026'
    special = re.compile('\033')

    # Name
    if vcard._get_first_names() or vcard._get_last_names():
        prefix = vcard._get_name_prefixes()
        first = vcard._get_first_names()
        middle = vcard._get_additional_names()
        last = vcard._get_last_names()
        suffix = vcard._get_name_suffixes()

        names = ''
        if config.config['contact table']['display'].lower() == 'first_name':
            if first:
                if prefix:
                    names += ' '.join(prefix)+' '
                names += ' '.join(first)+' '
            if middle:
                names += ' '.join(middle)+' '
            if last:
                names += ' '.join(last)
                if suffix:
                    names += ' '+' '.join(suffix)
        elif config.config['contact table']['display'].lower() == 'last_name':
            if last:
                names += ' '.join(last)
                if suffix:
                    names += ' '+' '.join(suffix)
            names += ', '
            if first:
                if prefix:
                    names += ' '.join(prefix)+' '
                names += ' '.join(first)+' '
            if middle:
                names += ' '.join(middle)
        else:
            raise ValueError('Invalid display config format')
        names = names.strip()
        max_width = console_width - 4
        if len(names) > max_width:
            names = names[:max_width-1]+ellip

    # Titles
    titles = vcard._get_titles()
    if len(titles) > 0:
        max_len_titles = max([len(x) for x in titles])
        max_len_titles = min(max_len_titles, console_width-4)
    else:
        max_len_titles = 0

    # Organisation
    orgs = vcard._get_organisations()
    if len(orgs) > 0:
        max_len_orgs = max([len(x) for x in orgs])
        max_len_orgs = min(max_len_orgs, console_width-4)
    else:
        max_len_orgs = 0

    # email addresses
    email = []
    if vcard.get_email_addresses().keys():
        email.append(color.BLUE+"E-Mail"+color.END)
        email.append(color.BLUE+"------"+color.END)
        for type, email_list in sorted(vcard.get_email_addresses().items(),
                                       key=lambda k: k[0].lower()):
            email += helpers.convert_to_yaml(type, email_list, 2, -1, False)

    # phone numbers
    phone = []
    if vcard.get_phone_numbers().keys():
        phone.append(color.BLUE+'Phone'+color.END)
        phone.append(color.BLUE+'-----'+color.END)
        for type, number_list in sorted(vcard.get_phone_numbers().items(),
                                        key=lambda k: k[0].lower()):
            phone += helpers.convert_to_yaml(type, number_list, 2, -1, False)

    # post addresses
    address = []
    if vcard._get_post_addresses().keys():
        address.append(color.BLUE+"Address"+color.END)
        address.append(color.BLUE+"-------"+color.END)
        for type, post_adr_list in sorted(vcard._get_formatted_post_addresses().items(),
                                          key=lambda k: k[0].lower()):
            lead_len = len(type)+4
            address.append('  '+type+': '+post_adr_list[0])
            for adr_line in post_adr_list[1:]:
                address.append(' '*lead_len+adr_line)


    # person related information
    general = []
    if vcard.get_birthday() is not None or vcard.get_anniversary() is not None \
            or vcard.get_nicknames() or vcard._get_roles():
        general.append(color.BLUE+"General"+color.END)
        general.append(color.BLUE+"-------"+color.END)
        if vcard.get_anniversary():
            general.append("  Anniversary: %s"
                            % vcard.get_formatted_anniversary())
        if vcard.get_birthday():
            general.append(
                "  Birthday: {}".format(vcard.get_formatted_birthday()))
        if vcard.get_nicknames():
            general += helpers.convert_to_yaml(
                "Nickname", vcard.get_nicknames(), 2, -1, False)
        if vcard._get_roles():
            general += helpers.convert_to_yaml(
                "Role", vcard._get_roles(), 2, -1, False)

    # private objects
    private = []
    if vcard._get_private_objects().keys():
        private.append(color.BLUE+"Private"+color.END)
        private.append(color.BLUE+"-------"+color.END)
        for object in vcard.supported_private_objects:
            if object in vcard._get_private_objects():
                private += helpers.convert_to_yaml(
                    object, vcard._get_private_objects().get(object), 2, -1,
                    False)

    # misc stuff
    misc = []
    if vcard._get_categories() or vcard._get_webpages() or vcard._get_notes():
        misc.append(color.BLUE+"Miscellaneous"+color.END)
        misc.append(color.BLUE+"-------------"+color.END)
        if vcard._get_categories():
            misc += helpers.convert_to_yaml(
                "Categories", vcard._get_categories(), 2, -1, False)
        if vcard._get_webpages():
            misc += helpers.convert_to_yaml(
                "Webpage", vcard._get_webpages(), 2, -1, False)
        if vcard._get_notes():
            misc += helpers.convert_to_yaml(
                "Note", vcard._get_notes()[0].split('\n'), 2, -1, False)

    # End matter
    end = []
    end.append("Address book: %s" % vcard.address_book.name)
    if vcard.get_uid():
        end.append("UID: {}".format(vcard.get_uid()))

    tab_width = max(len(names), max_len_titles, max_len_orgs)

    if console_width < 60 or len(address) == 0:
        two_col = False
        col_width = console_width - 4
    else:
        two_col = True
        col_width = (console_width-4)//2

    if len(names) > console_width-4:
        names = names[:console_width-4]+'…'
    print('╭─'+'─'*tab_width+'─╮')
    print('│ '+color.BOLD+names+color.END+' '*(tab_width-len(names))+' │')
    for title in titles:
        if len(title) > console_width-4:
            title = title[:console_width-5]+'…'
        print('│ '+title+' '*(tab_width-len(title))+' │')
    for org in orgs:
        if len(org) > console_width-4:
            org = org[:console_width-5]+'…'
        print('│ '+org+' '*(tab_width-len(org))+' │')
    print('├─'+'─'*tab_width+'─┴'+'─'*(console_width-tab_width-5)+'╮')

    if len(email) > 0 and len(phone) > 0:
        first_col = email + [''] + phone 
    elif len(email) > 0:
        first_col = email
    elif len(phone) > 0:
        first_col = phone
    else:
        first_col = []

    if two_col and len(address) > 0:
        second_col = address
    elif len(address) > 0:
        first_col += [''] + address

    if two_col:
        for line1, line2 in zip_longest(first_col, second_col):
            if line1 is None:
                line1 = ''
            if len(line1) > col_width:
                line1 = line1[:col_width-1]+u'\u2026'
            if special.search(line1):
                offset_width1 = col_width - len(line1) + 9
            else:
                offset_width1 = col_width - len(line1)

            if line2 is None:
                line2 = ''
            if len(line2) > col_width:
                line2 = line2[:col_width-1]+u'\u2026'
            if special.search(line2):
                offset_width2 = col_width - len(line2) + 9
            else:
                offset_width2 = col_width - len(line2)

            print('│ '+line1+' '*offset_width1+line2+' '*offset_width2+' │')
    else:
        for line in first_col:
            if len(line) > col_width:
                line = line[:col_width-1]+u'\u2026'
            if special.search(line):
                offset_width = col_width - len(line) + 9
            else:
                offset_width = col_width - len(line)
            print('│ '+line+' '*offset_width+' │')

    text_width = console_width - 4

    if len(general) > 0:
        print('│ '+' '*text_width+' │')
    for line in general:
        if len(line) > text_width:
            line = line[:text_width-1]+u'\u2026'
        if special.search(line):
            offset_width = text_width - len(line) + 9
        else:
            offset_width = text_width - len(line)
        print('│ '+line+' '*offset_width+' │')

    if len(private) > 0:
        print('│ '+' '*text_width+' │')
    for line in private:
        if len(line) > text_width:
            line = line[:text_width-1]+u'\u2026'
        if special.search(line):
            offset_width = text_width - len(line) + 9
        else:
            offset_width = text_width - len(line)
        print('│ '+line+' '*offset_width+' │')

    if len(misc) > 0:
        print('│ '+' '*text_width+' │')
    for line in misc:
        if len(line) > text_width:
            line = line[:text_width-1]+u'\u2026'
        if special.search(line):
            offset_width = text_width - len(line) + 9
        else:
            offset_width = text_width - len(line)
        print('│ '+line+' '*offset_width+' │')

    print('│ '+' '*text_width+' │')
    print('├─'+'─'*text_width+'─┤')
    for line in end:
        if len(line) > text_width:
            line = line[:text_width-1]+u'\u2026'
        if special.search(line):
            offset_width = text_width - len(line) + 9
        else:
            offset_width = text_width - len(line)
        print('│ '+line+' '*offset_width+' │')

    print('╰─'+'─'*text_width+'─╯')
