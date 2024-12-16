from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib import messages

from .models import Employee, Client, SalesPipelineStage, CustomUser, Product

# Регистрация моделей
admin.site.register(CustomUser)
admin.site.register(Employee)
admin.site.register(Client)
admin.site.register(SalesPipelineStage)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        """
        Удаление одного объекта.
        """
        if obj.sales.exists():
            raise ValidationError("Нельзя удалить продукт, связанный с продажами!")
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Массовое удаление объектов.
        """
        for obj in queryset:
            if obj.sales.exists():
                self.message_user(
                    request,
                    f"Нельзя удалить продукт '{obj.name}', так как он связан с продажами.",
                    level=messages.ERROR,
                )
            else:
                try:
                    obj.delete()
                except IntegrityError as e:
                    self.message_user(
                        request,
                        f"Ошибка при удалении продукта '{obj.name}': {str(e)}",
                        level=messages.ERROR,
                    )

    def has_delete_permission(self, request, obj=None):
        """
        Ограничьте удаление объектов при наличии связанных записей.
        """
        if obj and obj.sales.exists():
            return False
        return super().has_delete_permission(request, obj)
