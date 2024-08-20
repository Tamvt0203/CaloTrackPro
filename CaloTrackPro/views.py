# views.py
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from .serializers import LoginSerializer, RegisterSerializer, UserUpdateSerializer, FoodUserSerializer, FoodUserUpdateSerializer, WeightUpdateSerializer, UserInfoSerializer, FoodSerializer, FoodUserDetailSerializer
from rest_framework import status
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from .models import User,FoodUser, CaloHistory, Food
import datetime
class FoodUserDetailView(APIView):
    def post(self, request):
        userid = request.data.get('userid')
        date_str = request.data.get('date')

        if not userid or not date_str:
            return Response({"error": "Both userid and date must be provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the user to ensure they exist
        user = get_object_or_404(User, pk=userid)

        # Filter FoodUser records for the given user and date
        food_users = FoodUser.objects.filter(userid=user, date=date)
        serializer = FoodUserDetailSerializer(food_users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
class FoodListView(ListAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
class UserDetailView(APIView):
    def post(self, request):
        userid = request.data.get('userid')
        if not userid:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(userid=userid)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserInfoSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
class WeightUpdateView(APIView):
    def post(self, request):
        userid = request.data.get('userid')
        currentweight = request.data.get('currentweight')

        if not userid or currentweight is None:
            return Response({"status": "failed", "message": "Missing userid or currentweight"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(userid=userid)
        except User.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = WeightUpdateSerializer(user, data={'currentweight': currentweight})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "succeeded", "message": "Weight update successfully"}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class FoodUserUpdateView(APIView):
    def patch(self, request):
        try:
            food_user = FoodUser.objects.get(
                userid=request.data['userid'],
                date=request.data['date'],
                foodid=request.data['foodid'],
                meal=request.data['meal']
            )
        except FoodUser.DoesNotExist:
            return Response({'status': 'failed', 'message': 'FoodUser not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = FoodUserUpdateSerializer(food_user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            update_or_create_calo_history(food_user.userid, food_user.date)
            return Response({"status": "succeeded", "message": "Update FoodUser successfully"}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class FoodUserDeleteView(APIView):
    def delete(self, request):
        try:
            food_user = FoodUser.objects.get(
                userid=request.data['userid'],
                date=request.data['date'],
                foodid=request.data['foodid'],
                meal=request.data['meal']
            )
            food_user.delete()
            update_or_create_calo_history(food_user.userid, food_user.date)
            return Response({"status": "succeeded", "message": "FoodUser deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except FoodUser.DoesNotExist:
            return Response({'status': 'failed', 'message': 'FoodUser not found'}, status=status.HTTP_404_NOT_FOUND)

class FoodUserCreateView(APIView):
    def post(self, request):
        serializer = FoodUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            update_or_create_calo_history(serializer.instance.userid, serializer.instance.date)
            return Response({"status": "succeeded", "message": "Add FoodUser successfully"}, status=status.HTTP_201_CREATED)
        return Response({"status": "failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class RootView(APIView):
    def get(self, request):
        return Response({"message": "Connection successful"}, status=status.HTTP_200_OK)
class UserUpdateView(APIView):
    def post(self, request, userid):
        try:
            user = User.objects.get(userid=userid)
        except User.DoesNotExist:
            return Response({"status": "failed", "message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "succeeded", "message": "User update successfully"}, status=status.HTTP_200_OK)
        return Response({"status": "failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    return Response({
                        'status': 'succeeded',
                        'message': 'Login successful',
                        'userid': user.userid
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'status': 'failed',
                        'message': 'Login failed',
                        'userid': ''
                    }, status=status.HTTP_401_UNAUTHORIZED)  # Consider using HTTP_401_UNAUTHORIZED
            except User.DoesNotExist:
                return Response({
                    'status': 'failed',
                    'message': 'User not found',
                    'userid': ''
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'status': 'failed',
                'message': 'Invalid data',
                'userid': ''
            }, status=status.HTTP_400_BAD_REQUEST)
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'succeeded',
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'failed',
                'message': 'Registration failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
def update_or_create_calo_history(userid, date):
    total_calories = FoodUser.objects.filter(userid=userid, date=date).aggregate(Sum('foodtotalcalo'))['foodtotalcalo__sum'] or 0
    CaloHistory.objects.update_or_create(
        userid=userid, date=date,
        defaults={'datetotalcalo': total_calories}
    )