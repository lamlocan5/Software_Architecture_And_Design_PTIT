from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User, Group
from .models import Customer, Staff, Manager
from .serializers import CustomerSerializer, StaffSerializer, ManagerSerializer, UserSerializer

# ── JWT Customize to include role ──
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        
        # Determine role and profile ID
        role = 'customer'
        profile_id = None
        
        if user.is_superuser:
            role = 'admin'
        elif hasattr(user, 'manager_profile'):
            role = 'manager'
            profile_id = user.manager_profile.id
        elif hasattr(user, 'staff_profile'):
            role = 'staff'
            profile_id = user.staff_profile.id
        elif hasattr(user, 'customer_profile'):
            role = 'customer'
            profile_id = user.customer_profile.id
            
        token['role'] = role
        token['profile_id'] = profile_id
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# ── API Me view ──
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = 'customer'
        profile_id = None

        if user.is_superuser:
            role = 'admin'
        elif hasattr(user, 'manager_profile'):
            role = 'manager'
            profile_id = user.manager_profile.id
        elif hasattr(user, 'staff_profile'):
            role = 'staff'
            profile_id = user.staff_profile.id
        elif hasattr(user, 'customer_profile'):
            role = 'customer'
            profile_id = user.customer_profile.id

        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.first_name or user.username,
            'role': role,
            'profile_id': profile_id,
            'is_superuser': user.is_superuser
        })

# ── Customers ─────────────────────────────────────────────────────────────
class CustomerListCreate(APIView):
    def get(self, request):
        customers = Customer.objects.all()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password', 'customer123')

        if not name or not email:
            return Response({'error': 'Name and Email are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create Django User if not exists
        user = User.objects.filter(username=email).first()
        if not user:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )

        customer, created = Customer.objects.get_or_create(
            email=email,
            defaults={'name': name, 'user': user}
        )
        if not created:
            customer.name = name
            customer.user = user
            customer.save()

        # Publish customer_created event asynchronously (cart creation & welcome notification)
        try:
            from .event_broker import publish_event
            publish_event('customer_created', {
                'customer_id': customer.id,
                'email': email,
                'name': name
            })
        except Exception as e:
            print(f"[User Service] Failed to publish customer_created event: {e}")

        return Response(CustomerSerializer(customer).data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

# ── Staff ─────────────────────────────────────────────────────────────────
class StaffListCreate(APIView):
    def get(self, request):
        staff = Staff.objects.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password', 'staff123')

        if not name or not email:
            return Response({'error': 'Name and Email are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=email).first()
        if not user:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            staff_group, _ = Group.objects.get_or_create(name='staff')
            user.groups.add(staff_group)

        staff, created = Staff.objects.get_or_create(
            email=email,
            defaults={'name': name, 'user': user}
        )
        if not created:
            staff.name = name
            staff.user = user
            staff.save()

        return Response(StaffSerializer(staff).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class StaffDetail(APIView):
    def get_object(self, pk):
        try:
            return Staff.objects.get(pk=pk)
        except Staff.DoesNotExist:
            return None

    def get(self, request, pk):
        staff = self.get_object(pk)
        if not staff:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(StaffSerializer(staff).data)

    def patch(self, request, pk):
        staff = self.get_object(pk)
        if not staff:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        
        active = request.data.get('active')
        name = request.data.get('name')
        email = request.data.get('email')

        if active is not None:
            staff.active = active
            if staff.user:
                staff.user.is_active = active
                staff.user.save()
        if name is not None:
            staff.name = name
            if staff.user:
                staff.user.first_name = name
                staff.user.save()
        if email is not None:
            staff.email = email
            if staff.user:
                staff.user.username = email
                staff.user.email = email
                staff.user.save()

        staff.save()
        return Response(StaffSerializer(staff).data)

    def delete(self, request, pk):
        staff = self.get_object(pk)
        if not staff:
            return Response({'error': 'Staff not found'}, status=status.HTTP_404_NOT_FOUND)
        if staff.user:
            staff.user.delete()
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ── Managers ──────────────────────────────────────────────────────────────
class ManagerListCreate(APIView):
    def get(self, request):
        managers = Manager.objects.all()
        serializer = ManagerSerializer(managers, many=True)
        return Response(serializer.data)

    def post(self, request):
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password', 'manager123')

        if not name or not email:
            return Response({'error': 'Name and Email are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=email).first()
        if not user:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name
            )
            manager_group, _ = Group.objects.get_or_create(name='manager')
            user.groups.add(manager_group)

        manager, created = Manager.objects.get_or_create(
            email=email,
            defaults={'name': name, 'user': user}
        )
        if not created:
            manager.name = name
            manager.user = user
            manager.save()

        return Response(ManagerSerializer(manager).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class ManagerDetail(APIView):
    def get_object(self, pk):
        try:
            return Manager.objects.get(pk=pk)
        except Manager.DoesNotExist:
            return None

    def get(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ManagerSerializer(manager).data)

    def patch(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        
        active = request.data.get('active')
        name = request.data.get('name')
        email = request.data.get('email')

        if active is not None:
            manager.active = active
            if manager.user:
                manager.user.is_active = active
                manager.user.save()
        if name is not None:
            manager.name = name
            if manager.user:
                manager.user.first_name = name
                manager.user.save()
        if email is not None:
            manager.email = email
            if manager.user:
                manager.user.username = email
                manager.user.email = email
                manager.user.save()

        manager.save()
        return Response(ManagerSerializer(manager).data)

    def delete(self, request, pk):
        manager = self.get_object(pk)
        if not manager:
            return Response({'error': 'Manager not found'}, status=status.HTTP_404_NOT_FOUND)
        if manager.user:
            manager.user.delete()
        manager.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# ── Helper auth endpoint ──
class VerifyUserCredentials(APIView):
    def post(self, request):
        email = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        
        from django.contrib.auth import authenticate
        user = authenticate(username=email, password=password)
        if user:
            role = 'customer'
            profile_id = None
            if user.is_superuser:
                role = 'admin'
            elif hasattr(user, 'manager_profile'):
                role = 'manager'
                profile_id = user.manager_profile.id
            elif hasattr(user, 'staff_profile'):
                role = 'staff'
                profile_id = user.staff_profile.id
            elif hasattr(user, 'customer_profile'):
                role = 'customer'
                profile_id = user.customer_profile.id

            return Response({
                'valid': True,
                'user_id': user.id,
                'email': user.email,
                'name': user.first_name or user.username,
                'is_superuser': user.is_superuser,
                'role': role,
                'profile_id': profile_id
            })
        return Response({'valid': False}, status=status.HTTP_400_BAD_REQUEST)


class AuthVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = 'customer'
        profile_id = ''

        if user.is_superuser:
            role = 'admin'
        elif hasattr(user, 'manager_profile'):
            role = 'manager'
            profile_id = str(user.manager_profile.id)
        elif hasattr(user, 'staff_profile'):
            role = 'staff'
            profile_id = str(user.staff_profile.id)
        elif hasattr(user, 'customer_profile'):
            role = 'customer'
            profile_id = str(user.customer_profile.id)

        response = Response({'status': 'authenticated'})
        response['X-User-Id'] = str(user.id)
        response['X-User-Username'] = user.username
        response['X-User-Email'] = user.email
        response['X-User-Role'] = role
        response['X-User-Profile-Id'] = profile_id
        response['X-User-Superuser'] = '1' if user.is_superuser else '0'
        return response

