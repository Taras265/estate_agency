import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from django.core.management import BaseCommand
from django.contrib.auth.models import Permission

from accounts.models import CustomGroup


def parse_group_element(group_element: Element) -> tuple[str, list[str]]:
    """
    Парсить xml елемент <Group></Group> та
    повертає назву групи і список назв прав для неї.
    """
    permission_codenames = []

    group_name = group_element.findtext("Name")
    if not group_name:
        raise ValueError("You didn't specify a group name.")

    permission_list_element = group_element.find("PermissionList")
    if permission_list_element is None:
        return group_name, permission_codenames
    
    for permission_element in permission_list_element.findall("Permission"):
        codename = permission_element.text
        if not codename:
            raise ValueError("You didn't specify a permission codename.")
        
        permission_codenames.append(codename)

    return group_name, permission_codenames


class Command(BaseCommand):
    help = "Додає групи та користувачів з файлів 'xml/Groups.xml' та 'xml/Users.xml' до бази даних."

    def handle(self, *args, **options):
        self.stdout.write("Filling groups...")

        root = ET.parse("xml/Groups.xml").getroot()
        group_and_perm_names = dict(map(parse_group_element, root.findall("Group")))
        
        groups = [CustomGroup(name=group_name) for group_name in group_and_perm_names.keys()]
        for group in groups:
            group.save()

        for group, perm_codenames in zip(groups, group_and_perm_names.values()):
            if len(perm_codenames) == 0:
                continue

            permissions = Permission.objects.filter(codename__in=perm_codenames)
            for permission in permissions.all():
                group.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS("Groups and users filled successfully!"))