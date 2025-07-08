import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from xml.etree.ElementTree import Element

from django.contrib.auth.models import Permission
from django.core.management import BaseCommand

from accounts.models import CustomGroup, CustomUser
from handbooks.models import FilialAgency


@dataclass
class GroupData:
    name: str
    permissions: list[str] = field(default_factory=list)


@dataclass
class UserData:
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""
    filials: list[str] = field(default_factory=list)
    phone_numbers: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)


def parse_group_element(group_element: Element) -> GroupData:
    """Парсить xml елемент <Group></Group>"""
    group = GroupData(name=group_element.findtext("Name"))

    perm_list_element = group_element.find("PermissionList")
    if perm_list_element is None:
        return group

    group.permissions += [
        elem.text
        for elem in perm_list_element.findall("Permission")
        if elem.text is not None
    ]

    return group


def parse_user_element(user_element: Element) -> UserData:
    """Парсить xml елемент <User></User>"""
    user = UserData(
        email=user_element.findtext("Email"),
        password=user_element.findtext("Password"),
        first_name=user_element.findtext("FirstName"),
        last_name=user_element.findtext("LastName"),
    )

    filial_list_element = user_element.find("FilialList")
    if filial_list_element is not None:
        user.filials += [
            element.text for element in filial_list_element.findall("Filial")
        ]

    phone_list_element = user_element.find("PhoneNumberList")
    if phone_list_element is not None:
        user.phone_numbers += [
            element.text for element in phone_list_element.findall("PhoneNumber")
        ]

    group_list_element = user_element.find("GroupList")
    if group_list_element is not None:
        user.groups += [element.text for element in group_list_element.findall("Group")]

    return user


class Command(BaseCommand):
    help = "Додає групи та користувачів з файлів 'xml/Groups.xml' та 'xml/Users.xml' до бази даних."

    def handle(self, *args, **options):
        self.stdout.write("Filling groups...")

        root = ET.parse("xml/Groups.xml").getroot()
        groups_data = list(map(parse_group_element, root.findall("Group")))

        if any(group.name == "" for group in groups_data):
            raise ValueError("You didn't specify a group name.")

        groups = [CustomGroup(name=group.name) for group in groups_data]
        for group in groups:
            group.save()

        for i, group_data in enumerate(groups_data):
            if len(group_data.permissions) == 0:
                continue

            perms = Permission.objects.filter(codename__in=group_data.permissions)
            groups[i].permissions.set(perms)

        self.stdout.write("Groups filled successfully!")
        self.stdout.write("Filling users...")

        users_root = ET.parse("xml/Users.xml").getroot()
        users_data = list(map(parse_user_element, users_root.findall("User")))

        if any(user.email == "" for user in users_data):
            raise ValueError("You didn't specify user email.")

        if any(user.password == "" for user in users_data):
            raise ValueError("You didn't specify user password.")

        users = [
            CustomUser(
                email=user.email, first_name=user.first_name, last_name=user.last_name
            )
            for user in users_data
        ]
        for i, user_data in enumerate(users_data):
            users[i].set_password(user_data.password)

        users = CustomUser.objects.bulk_create(users)

        for i, user_data in enumerate(users_data):
            users[i].save()
            if user_data.filials:
                filials = FilialAgency.objects.filter(filial_agency__in=user_data.filials)
                users[i].filials.set(filials)

            if user_data.groups:
                groups = CustomGroup.objects.filter(name__in=user_data.groups)
                users[i].groups.set(groups)

            for phone_number in user_data.phone_numbers:
                users[i].phone_numbers.create(number=phone_number)

        self.stdout.write(self.style.SUCCESS("Groups and users filled successfully!"))
