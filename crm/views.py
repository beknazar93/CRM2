import json
import logging
from datetime import timedelta

from django.core.mail import send_mail
from django.db.models import Sum
from django.http import JsonResponse
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Employee, Client, SalesPipelineStage, CustomUser, Product, Sale, ChatMessage

from .serializers import EmployeeSerializer, ClientSerializer, SalesPipelineStageSerializer, UserSerializer, RegisterSerializer, ProductSerializer, SaleSerializer


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            return Response({"dashboard": "Administrator Dashboard"})
        elif user.role == 'client_manager':
            return Response({"dashboard": "Client Manager Dashboard"})
        elif user.role == 'product_manager':
            return Response({"dashboard": "Product Manager Dashboard"})
        elif user.role == 'hr_manager':
            return Response({"dashboard": "HR Manager Dashboard"})
        elif user.role == 'employee':
            return Response({"dashboard": "Employee Dashboard"})
        return Response({"error": "Unknown role"}, status=400)


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    # Метод удаления сотрудника
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Employee deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class ClientManagerDashboardView(View):
    def get(self, request):
        # Реальные данные можно заменить на актуальные для клиента
        return JsonResponse({
            "message": "Добро пожаловать в панель менеджера по работе с клиентами",
            "tasks": [
                {"id": 1, "task": "Подготовить отчет для клиента"},
                {"id": 2, "task": "Созвон с клиентом ABC"},
            ]
        })


logger = logging.getLogger(__name__)


class IsAdminOrHR(BasePermission):
    def has_permission(self, request, view):
        print(f"Пользователь: {request.user}, Роль: {request.user.role}")
        return request.user.is_authenticated and (
            request.user.role in ['admin', 'hr_manager', 'client_manager']
        )
class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, IsAdminOrHR]

    def list(self, request, *args, **kwargs):
        print("Authorization header:", request.headers.get('Authorization'))
        logger.info(f"Запрос от пользователя {request.user.username} с ролью {request.user.role}")
        return super().list(request, *args, **kwargs)

    # Метод удаления клиента
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Client deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        sport_category = request.data.get('sport_category')
        month = request.data.get('month')
        year = request.data.get('year')

        # Проверяем существование клиента с теми же параметрами
        if Client.objects.filter(name=name, sport_category=sport_category, month=month, year=year).exists():
            raise ValidationError({
                "error": f"Клиент с именем '{name}' уже добавлен в категорию '{sport_category}' на {month} {year}."
            })

        return super().create(request, *args, **kwargs)

logger = logging.getLogger(__name__)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cleanup_old_clients(request):
    logger.info("Запрос на очистку старых клиентов получен.")
    cutoff_date = now() - timedelta(days=60)  # 2 месяца
    old_clients = Client.objects.filter(created_at__lt=cutoff_date)
    deleted_count = old_clients.count()
    logger.info(f"Найдено {deleted_count} клиентов для удаления.")
    old_clients.delete()
    logger.info(f"{deleted_count} клиентов успешно удалено.")
    return Response({"message": f"{deleted_count} клиентов удалено."}, status=200)

class SalesPipelineStageViewSet(viewsets.ModelViewSet):
    queryset = SalesPipelineStage.objects.all()
    serializer_class = SalesPipelineStageSerializer

class IsProductManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'product_manager,hr_manager'

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProductManager, IsAdminOrHR]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Ошибки валидации:", serializer.errors)  # Логирование ошибок
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        print("Authorization header:", request.headers.get('Authorization'))
        return super().list(request, *args, **kwargs)

class SaleViewSet(ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_analytics(request):
    data = {
        "total_clients": Client.objects.count(),
        "total_revenue": Sale.objects.aggregate(Sum('sale_price'))['sale_price__sum'],
    }
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_dashboard(request):
    employee = request.user
    data = {
        "name": employee.username,
        "tasks": employee.tasks.all().values(),
        "clients": employee.clients.all().values(),
    }
    return Response(data)


@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_name = data.get('user_name')
            message = data.get('message')

            if user_name and message:
                # Сохранение сообщения в базу
                chat_message = ChatMessage.objects.create(user_name=user_name, message=message)

                # Отправка сообщения по email HR-менеджерам
                send_mail(
                    subject=f"Новое сообщение от {user_name}",
                    message=f"Сообщение: {message}\n\nОтправлено: {chat_message.timestamp}",
                    from_email='no-reply@yourdomain.com',
                    recipient_list=['hr_manager@yourdomain.com'],
                )

                return JsonResponse({'status': 'success', 'message': 'Сообщение отправлено менеджерам.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Введите имя и сообщение.'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Недопустимый метод запроса.'}, status=400)