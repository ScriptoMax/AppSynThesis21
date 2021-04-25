from django.db import models
from django.db.models import Max


class Employee(models.Model):

    class EmployeeStatus(models.TextChoices):
        ACTIVE = 'Active'
        ON_LEAVE = 'On leave'
        QUITED = 'Quited'

    id = models.PositiveIntegerField(primary_key=True, default=0)
    status = models.CharField(max_length=8,
                              choices=EmployeeStatus.choices,
                              default=EmployeeStatus.ACTIVE)
    first_name = models.CharField(max_length=20)
    second_name = models.CharField(max_length=20, blank=True)
    last_name = models.CharField(max_length=20)
    user_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    dial_extension = models.IntegerField(default=1)
    token = models.CharField(max_length=50, default='')


class RealTimeRecognitionControl(models.Model):
    host_ip_address = models.CharField(max_length=50)
    current_user = models.ForeignKey(Employee,
                                     related_name='%(class)s',
                                     blank=True,
                                     null=True,
                                     on_delete=models.SET_NULL)
    websocket_connection_address = models.CharField(max_length=50)
    stasis_instance_name = models.CharField(max_length=10)
    stasis_pid = models.PositiveIntegerField(default=1)
    monitor_file_name = models.CharField(max_length=80)
    websocket_pid = models.PositiveIntegerField(default=1)


class BaseCategory(models.Model):
    code = models.PositiveIntegerField(primary_key=True, default=100)
    name = models.CharField(max_length=60)


class Subcategory(models.Model):
    code = models.PositiveIntegerField(primary_key=True, default=101)
    base_category_code = models.ForeignKey(BaseCategory,
                                           related_name='%(class)s',
                                           on_delete=models.PROTECT)
    name = models.CharField(max_length=120)


class CallHandlingReport(models.Model):

    class CustomerType(models.TextChoices):
        NONE = 'NONE'
        INDIVIDUAL = 'IND'
        CORPORATE_B2B = 'CORP <B2B>'
        CORPORATE_B2G = 'CORP <B2G>'

    employee = models.ForeignKey(Employee,
                                 related_name='%(class)s',
                                 on_delete=models.PROTECT)
    caller_phone = models.CharField(max_length=20)
    caller_customer_type = models.CharField(max_length=10,
                                            choices=CustomerType.choices,
                                            default=CustomerType.INDIVIDUAL)
    caller_contract_region = models.CharField(max_length=30, blank=True)
    registered_on = models.DateTimeField(auto_now_add=True)
    base_category_code = models.ForeignKey(BaseCategory,
                                           related_name='%(class)s',
                                           on_delete=models.PROTECT,
                                           default=200)
    subcategory_code = models.ForeignKey(Subcategory,
                                         related_name='%(class)s',
                                         on_delete=models.PROTECT,
                                         default=201,
                                         blank=True,
                                         null=True)
    extended_notes = models.TextField(blank=True)

    @classmethod
    def set_unique_child_id(cls):

        pk_list = list()

        max_pk_cat1 = CommonInfoProvisionReport.objects.all().aggregate(Max('report_id'))['report_id__max']
        max_pk_cat1 = 0 if max_pk_cat1 is None else max_pk_cat1
        pk_list.append(max_pk_cat1)

        max_pk_cat2 = UserAccountInfoReport.objects.all().aggregate(Max('report_id'))['report_id__max']
        max_pk_cat2 = 0 if max_pk_cat2 is None else max_pk_cat2
        pk_list.append(max_pk_cat2)

        max_pk_cat3 = UserAccountControlReport.objects.all().aggregate(Max('report_id'))['report_id__max']
        max_pk_cat3 = 0 if max_pk_cat3 is None else max_pk_cat3
        pk_list.append(max_pk_cat3)

        max_pk_cat4 = TechnicalIssueReport.objects.all().aggregate(Max('report_id'))['report_id__max']
        max_pk_cat4 = 0 if max_pk_cat4 is None else max_pk_cat4
        pk_list.append(max_pk_cat4)

        max_pk_cat5 = ProspectDealReport.objects.all().aggregate(Max('report_id'))['report_id__max']
        max_pk_cat5 = 0 if max_pk_cat5 is None else max_pk_cat5
        pk_list.append(max_pk_cat5)

        max_pk_cat6 = CustomerDiscontentReport.objects.all().aggregate(Max('report_id'))['report_id__max']
        max_pk_cat6 = 0 if max_pk_cat6 is None else max_pk_cat6
        pk_list.append(max_pk_cat6)

        max_pk_cat7 = ContactCancelReport.objects.all().aggregate(Max('report_id'))['report_id__max']
        max_pk_cat7 = 0 if max_pk_cat7 is None else max_pk_cat7
        pk_list.append(max_pk_cat7)

        uuid = max(pk_list) + 1
        pk_list.clear()
        return uuid

    class Meta:
        abstract = True

'''
class UniqueIdGenerator(models.Model):
    uuid = models.PositiveIntegerField(default=10)
'''


class ServiceCategory(models.Model):

    class CategoryChoices(models.TextChoices):
        TARIFF = 'Тарифный план'
        VOICE_SERVICE = 'Голосовая связь'
        SMS_MMS_SERVICE = 'SMS/MMS'
        INTERNET_PROVIDING = 'Интернет'
        PAY_BANKING_SERVICE = 'Платежи/переводы'
        EXTRA_SUBSCRIPTION_SERVICE = 'Подписки на контент'
        SELF_SERVICE_PROVIDING = 'Сервисы самообслуживания'
        ROAMING = 'Услуги для роуминга'

    name = models.CharField(primary_key=True,
                            max_length=25,
                            choices=CategoryChoices.choices,
                            default=CategoryChoices.TARIFF)


class ServiceRange(models.Model):

    code = models.PositiveIntegerField(primary_key=True, default=1000)
    name = models.CharField(max_length=100)
    category = models.ForeignKey(ServiceCategory,
                                 related_name='%(class)s',
                                 on_delete=models.PROTECT)


class ContactCancelReport(CallHandlingReport):

    class ContactCancelGround(models.TextChoices):
        WRONG_UNKNOWN_BASIC_REQUISITES = 'Wrong / unknown basic security requisites'
        WRONG_UNKNOWN_CALLER_PASSWORD = 'Wrong / unknown caller password'

    report_id = models.PositiveIntegerField(default=CallHandlingReport.set_unique_child_id)
    cancel_ground = models.CharField(max_length=41,
                                     choices=ContactCancelGround.choices,
                                     default=ContactCancelGround.WRONG_UNKNOWN_BASIC_REQUISITES)


class CommonInfoProvisionReport(CallHandlingReport):
    report_id = models.PositiveIntegerField(default=CallHandlingReport.set_unique_child_id)
    service_category = models.ForeignKey(ServiceCategory,
                                         related_name='%(class)s',
                                         on_delete=models.PROTECT,
                                         blank=True,
                                         null=True)
    service_code = models.ForeignKey(ServiceRange,
                                     related_name='%(class)s',
                                     on_delete=models.PROTECT,
                                     blank=True,
                                     null=True)


class UserAccountInfoReport(CallHandlingReport):
    report_id = models.PositiveIntegerField(default=CallHandlingReport.set_unique_child_id)
    service_category = models.ForeignKey(ServiceCategory,
                                         related_name='%(class)s',
                                         on_delete=models.PROTECT,
                                         blank=True,
                                         null=True)
    service_code = models.ForeignKey(ServiceRange,
                                     related_name='%(class)s',
                                     on_delete=models.PROTECT,
                                     blank=True,
                                     null=True)


class UserAccountControlReport(CallHandlingReport):
    report_id = models.PositiveIntegerField(default=CallHandlingReport.set_unique_child_id)
    service_category = models.ForeignKey(ServiceCategory,
                                         related_name='%(class)s',
                                         on_delete=models.PROTECT,
                                         blank=True,
                                         null=True)
    enabled_service_code = models.ForeignKey(ServiceRange,
                                             related_name='%(class)s_on',
                                             on_delete=models.PROTECT,
                                             blank=True,
                                             null=True)
    disabled_service_code = models.ForeignKey(ServiceRange,
                                              related_name='%(class)s_off',
                                              on_delete=models.PROTECT,
                                              blank=True,
                                              null=True)


class TechnicalIssueReport(CallHandlingReport):
    report_id = models.PositiveIntegerField(default=CallHandlingReport.set_unique_child_id)
    service_category = models.ForeignKey(ServiceCategory,
                                         related_name='%(class)s',
                                         on_delete=models.PROTECT,
                                         blank=True,
                                         null=True)
    service_code = models.ForeignKey(ServiceRange,
                                     related_name='%(class)s',
                                     on_delete=models.PROTECT,
                                     blank=True,
                                     null=True)
    user_equipment = models.CharField(max_length=80)
    start_timestamp = models.DateTimeField()
    region = models.CharField(max_length=30, blank=True)
    area = models.CharField(max_length=50)
    street = models.CharField(max_length=30, blank=True)
    building = models.CharField(max_length=10, blank=True)
    main_issue_effect = models.CharField(max_length=80)


class ProspectDealReport(CallHandlingReport):
    report_id = models.PositiveIntegerField(default=CallHandlingReport.set_unique_child_id)
    service_category = models.ForeignKey(ServiceCategory,
                                         related_name='%(class)s',
                                         on_delete=models.PROTECT,
                                         blank=True,
                                         null=True)
    service_code = models.ForeignKey(ServiceRange,
                                     related_name='%(class)s',
                                     on_delete=models.PROTECT,
                                     blank=True,
                                     null=True)
    contact_person = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    contact_time_period = models.DateTimeField()


class CustomerDiscontentReport(CallHandlingReport):

    class BusinessUnit(models.TextChoices):
        OWN_RETAIL_STORE = 'Own retail store'
        PARTNER_RETAIL_STORE = 'Partner retail store'
        CONTACT_CENTER = 'Contact center'

    report_id = models.PositiveIntegerField(default=CallHandlingReport.set_unique_child_id)
    involved_employee = models.CharField(max_length=60, blank=True)
    business_unit = models.CharField(max_length=20,
                                     blank=True,
                                     choices=BusinessUnit.choices,
                                     default=BusinessUnit.OWN_RETAIL_STORE)
    store_address = models.CharField(max_length=100, blank=True)
    service_category = models.ForeignKey(ServiceCategory,
                                         related_name='%(class)s',
                                         on_delete=models.PROTECT,
                                         blank=True,
                                         null=True)
    case_service_code = models.ForeignKey(ServiceRange,
                                          related_name='%(class)s',
                                          on_delete=models.PROTECT,
                                          blank=True,
                                          null=True)
    refunding_amount = models.FloatField(blank=True)