from django.contrib import admin
from unchained import models

admin.site.register(models.Employee)
admin.site.register(models.RealTimeRecognitionControl)
admin.site.register(models.BaseCategory)
admin.site.register(models.Subcategory)
admin.site.register(models.ServiceRange)
admin.site.register(models.ServiceCategory)
admin.site.register(models.CommonInfoProvisionReport)
admin.site.register(models.UserAccountInfoReport)
admin.site.register(models.UserAccountControlReport)
admin.site.register(models.TechnicalIssueReport)
admin.site.register(models.ProspectDealReport)
admin.site.register(models.CustomerDiscontentReport)
admin.site.register(models.ContactCancelReport)