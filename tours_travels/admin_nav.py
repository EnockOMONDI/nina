from django.urls import reverse


def adminside_package_list(request=None):
    return reverse("admin:adminside_package_changelist")


def adminside_hotel_list(request=None):
    return reverse("admin:adminside_hotel_changelist")


def blog_post_list(request=None):
    return reverse("admin:blog_post_changelist")


def blog_category_list(request=None):
    return reverse("admin:blog_category_changelist")


def users_contact_list(request=None):
    return reverse("admin:users_contactinquiry_changelist")


def users_corporate_list(request=None):
    return reverse("admin:users_corporateinquiry_changelist")


def users_mice_list(request=None):
    return reverse("admin:users_miceinquiry_changelist")


def users_student_list(request=None):
    return reverse("admin:users_studenttravelinquiry_changelist")


def users_ngo_list(request=None):
    return reverse("admin:users_ngotravelinquiry_changelist")


def auth_user_list(request=None):
    return reverse("admin:auth_user_changelist")


def auth_group_list(request=None):
    return reverse("admin:auth_group_changelist")
