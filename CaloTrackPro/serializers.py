from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils.timezone import now
from django.utils import timezone
from .models import User, FoodUser, Food, WeightHistory, CaloHistory
class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['foodid', 'foodname', 'foodunit', 'foodcalo']

class FoodUserDetailSerializer(serializers.ModelSerializer):
    foodname = serializers.CharField(source='foodid.foodname')
    foodunit = serializers.CharField(source='foodid.foodunit')

    class Meta:
        model = FoodUser
        fields = ['meal', 'foodid', 'foodname', 'foodunit', 'quantity', 'foodtotalcalo']
class UserInfoSerializer(serializers.ModelSerializer):
    today_consumed_calo = serializers.SerializerMethodField()
    recent_weight_history = serializers.SerializerMethodField()
    calo_last_7_days = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['userid', 'username', 'dateofbirth', 'currentweight', 'height', 'gender', 'recommendcalo', 'today_consumed_calo', 'recent_weight_history', 'calo_last_7_days']

    def get_today_consumed_calo(self, obj):
        today = timezone.now().date()
        try:
            calo_record = CaloHistory.objects.get(userid=obj, date=today)
            return calo_record.datetotalcalo
        except CaloHistory.DoesNotExist:
            return 0

    def get_recent_weight_history(self, obj):
        one_month_ago = timezone.now().date() - timezone.timedelta(days=30)
        weight_records = WeightHistory.objects.filter(userid=obj, date__gte=one_month_ago).order_by('date')
        return [{'date': record.date, 'weight': record.weight} for record in weight_records]

    def get_calo_last_7_days(self, obj):
        seven_days_ago = timezone.now().date() - timezone.timedelta(days=7)
        calo_records = CaloHistory.objects.filter(userid=obj, date__gte=seven_days_ago).order_by('date')
        return [{'date': record.date, 'calories': record.datetotalcalo} for record in calo_records]
class WeightUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['currentweight']

    def update(self, instance, validated_data):
        instance.currentweight = validated_data.get('currentweight', instance.currentweight)

        # Calculate the user's age
        age = now().year - instance.dateofbirth.year - ((now().month, now().day) < (instance.dateofbirth.month, instance.dateofbirth.day))

        # Calculate recommended calories based on gender and formula
        if instance.gender == 'Male':
            instance.recommendcalo = 66 + (13.7 * instance.currentweight) + (5 * instance.height) - (6.76 * age)
        else:
            instance.recommendcalo = 655 + (9.6 * instance.currentweight) + (1.8 * instance.height) - (4.7 * age)

        instance.save()

        # Update or create a weight history entry for the current date
        WeightHistory.objects.update_or_create(
            userid=instance,
            date=now().date(),
            defaults={'weight': instance.currentweight}
        )

        return instance
class FoodUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodUser
        fields = ['quantity', 'foodtotalcalo']

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        # Recalculate the total calories
        food_calo = instance.foodid.foodcalo
        instance.foodtotalcalo = instance.quantity * food_calo
        instance.save()
        return instance
class FoodUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodUser
        fields = ['userid', 'date', 'foodid', 'meal', 'quantity']

    def create(self, validated_data):
        # Retrieve the related Food object based on the provided foodid
        food_item = Food.objects.get(foodid=validated_data['foodid'].foodid)
        
        # Calculate total calories
        foodtotalcalo = validated_data['quantity'] * food_item.foodcalo

        # Update or create the FoodUser instance
        food_user, created = FoodUser.objects.update_or_create(
            userid=validated_data['userid'],
            date=validated_data['date'],
            foodid=validated_data['foodid'],
            meal=validated_data['meal'],
            defaults={'quantity': validated_data['quantity'], 'foodtotalcalo': foodtotalcalo}
        )
        
        return food_user

    def to_representation(self, instance):
        # Include foodtotalcalo when retrieving the instance
        ret = super().to_representation(instance)
        ret['foodtotalcalo'] = instance.foodtotalcalo
        return ret
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255)
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def validate_password(self, value):
        # Ensure the password is hashed before saving
        return make_password(value)

    def validate_username(self, value):
        # Check if the username already exists
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['dateofbirth', 'currentweight', 'height', 'gender']

    def validate_dateofbirth(self, value):
        if value > now().date():
            raise serializers.ValidationError("The date of birth cannot be in the future.")
        return value

    def update(self, instance, validated_data):
        instance.dateofbirth = validated_data.get('dateofbirth', instance.dateofbirth)
        instance.currentweight = validated_data.get('currentweight', instance.currentweight)
        instance.height = validated_data.get('height', instance.height)
        instance.gender = validated_data.get('gender', instance.gender)

        # Calculate age
        age = now().year - instance.dateofbirth.year - ((now().month, now().day) < (instance.dateofbirth.month, instance.dateofbirth.day))

        # Calculate recommendcalo based on gender
        if instance.gender == 'Male':
            instance.recommendcalo = 66 + (13.7 * instance.currentweight) + (5 * instance.height) - (6.76 * age)
        else:
            instance.recommendcalo = 655 + (9.6 * instance.currentweight) + (1.8 * instance.height) - (4.7 * age)

        instance.save()

        # Update or create weight history
        weight_history, created = WeightHistory.objects.update_or_create(
            userid=instance,
            date=now().date(),  # Assuming updates happen based on current date
            defaults={'weight': instance.currentweight}
        )

        return instance