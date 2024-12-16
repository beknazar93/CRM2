from rest_framework import serializers
from .models import Employee, Client, SalesPipelineStage, CustomUser, Product, Sale


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'employee')
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class SalesPipelineStageSerializer(serializers.ModelSerializer):
    clients = ClientSerializer(many=True, read_only=True)

    class Meta:
        model = SalesPipelineStage
        fields = '__all__'


class SaleSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")  # Имя товара

    class Meta:
        model = Sale
        fields = ["id", "product", "product_name", "sale_date", "sale_price"]


class ProductSerializer(serializers.ModelSerializer):
    sales = SaleSerializer(many=True, read_only=True)  # Связанные продажи

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "purchase_price",
            "markup",
            "final_price",
            "purchase_date",
            "is_sold",
            "sale_date",
            "quantity",
            "sales",  # Поле для отображения истории продаж
        ]

    def validate(self, data):
        if data.get('quantity', 0) < 0:
            raise serializers.ValidationError("Количество товара не может быть отрицательным.")
        return data
