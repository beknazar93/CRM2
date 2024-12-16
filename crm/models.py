from django.contrib.auth.models import AbstractUser, User
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('client_manager', 'Client Manager'),
        ('product_manager', 'Product Manager'),
        ('hr_manager', 'HR Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='employee')


class Employee(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} || должность {self.position} || {self.email} || {self.phone}'


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, default="primer@gmail.com")
    phone = models.CharField(max_length=100)
    stage = models.CharField(max_length=100)
    payment = models.CharField(max_length=20, default='оплачено')
    price = models.CharField(max_length=20, default="2200")
    sport_category = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trainer = models.CharField(max_length=100, null=True, blank=True)
    year = models.CharField(max_length=100, null=True, blank=True)
    month = models.CharField(max_length=100, null=True, blank=True)
    day = models.CharField(max_length=100, null=True, blank=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        return f'{self.name} || {self.email} || {self.phone}'


class SalesPipelineStage(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    clients = models.ManyToManyField(Client, related_name='pipeline_stages')

    def __str__(self):
        return f'{self.name}  {self.description}'


class Product(models.Model):
    name = models.CharField(max_length=100)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    markup = models.DecimalField(max_digits=5, decimal_places=2)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    purchase_date = models.DateField()
    is_sold = models.BooleanField(default=False)
    sale_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Обновляем финальную цену на основе наценки
        self.final_price = self.purchase_price + (self.purchase_price * self.markup / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Sale(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # Используем PROTECT, чтобы избежать удаления связанного товара
        related_name="sales",
        verbose_name="Товар",
    )
    sale_date = models.DateField(verbose_name="Дата продажи")
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость продажи")

    def save(self, *args, **kwargs):
        if self.product:
            if self.product.is_sold:
                raise ValueError("Этот товар уже продан.")
            if self.product.quantity < 1:
                raise ValueError("Недостаточно товара на складе для продажи.")
            # Обновляем состояние товара при продаже
            self.product.is_sold = True
            self.product.sale_date = self.sale_date
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.sale_date}"
# models.py



class ChatMessage(models.Model):
    user_name = models.CharField(max_length=100)  # Имя пользователя
    message = models.TextField()  # Текст сообщения
    timestamp = models.DateTimeField(auto_now_add=True)  # Время отправки
    is_forwarded = models.BooleanField(default=False)  # Метка отправки HR

    def __str__(self):
        return f"{self.user_name}: {self.message[:30]}"

    @classmethod
    def as_view(cls):
        pass