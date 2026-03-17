from django.urls import reverse


def adminside_package_list(request=None):
    return reverse("admin:adminside_package_changelist")


def adminside_hotel_list(request=None):
    return reverse("admin:adminside_hotel_changelist")


def adminside_career_job_list(request=None):
    return reverse("admin:adminside_careerjob_changelist")


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


def users_career_application_list(request=None):
    return reverse("admin:users_careerapplication_changelist")


def users_package_quote_list(request=None):
    return reverse("admin:users_packagequoteinquiry_changelist")


def users_hotel_inquiry_list(request=None):
    return reverse("admin:users_hotelinquiry_changelist")


def auth_user_list(request=None):
    return reverse("admin:auth_user_changelist")


def auth_group_list(request=None):
    return reverse("admin:auth_group_changelist")


def _count_unread(model):
    return model.objects.filter(is_read=False).count()


def unread_contact_badge(request=None):
    from users.models import ContactInquiry

    return _count_unread(ContactInquiry)


def unread_corporate_badge(request=None):
    from users.models import CorporateInquiry

    return _count_unread(CorporateInquiry)


def unread_package_quote_badge(request=None):
    from users.models import PackageQuoteInquiry

    return _count_unread(PackageQuoteInquiry)


def unread_hotel_inquiry_badge(request=None):
    from users.models import HotelInquiry

    return _count_unread(HotelInquiry)


def unread_career_badge(request=None):
    from users.models import CareerApplication

    return _count_unread(CareerApplication)


def unread_mice_badge(request=None):
    from users.models import MICEInquiry

    return _count_unread(MICEInquiry)


def unread_student_badge(request=None):
    from users.models import StudentTravelInquiry

    return _count_unread(StudentTravelInquiry)


def unread_ngo_badge(request=None):
    from users.models import NGOTravelInquiry

    return _count_unread(NGOTravelInquiry)
