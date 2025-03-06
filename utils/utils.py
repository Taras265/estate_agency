from utils.const import TABLE_TO_APP, LIST_BY_USER, OBJECT_FIELDS


def have_permission_to_do(user, perm_type, handbook_type, obj, p=""):

    p_handbook_type = "".join(handbook_type.split("_"))
    has_perm = user.has_perm(f"{TABLE_TO_APP[handbook_type]}.{perm_type}_{p}{p_handbook_type}")
    if handbook_type in LIST_BY_USER.keys() and not has_perm:
        if isinstance(LIST_BY_USER[handbook_type], str):
            return check_own_perm_by_field(obj,
                                           LIST_BY_USER[handbook_type],
                                           user,
                                           f"{TABLE_TO_APP[handbook_type]}.{perm_type}_own_{p}{p_handbook_type}")
        else:
            for field in LIST_BY_USER[handbook_type]:
                has_perm = check_own_perm_by_field(obj,
                                                   field,
                                                   user,
                                                   f"{TABLE_TO_APP[handbook_type]}.{perm_type}_own_{p}{p_handbook_type}")

                if has_perm:
                    break

    return has_perm


def check_own_perm_by_field(obj, field, user, perm):
    if obj.get(f"{field}_id") == user.id:
        return user.has_perm(perm)
    return False


def model_to_dict(user, queryset, app, handbook_type, own=False):
    object_fields: list[str] | None = OBJECT_FIELDS.get(handbook_type)

    if object_fields:
        queryset = queryset.values(*object_fields)
    else:
        queryset = queryset.values()
    for instance in queryset:
        change_perm = user.has_perm(f"{app}.change_{handbook_type}")
        instance.update({
            "user_permissions": {
                "can_update": change_perm or user.has_perm(f"{app}.change_own_{handbook_type}")
                                    if own else change_perm
            }
        })
    return queryset
