from rest_framework import serializers
from RationSystem.models import RationUser



# user creation Serializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    #we are writing this because we need comfrim password field in outr Ragistration Request
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model = RationUser
        fields =['email','name','tc','password','password2']

        extra_kwargs={
            'password':{'write_only':True }
        }

    # Validation Password and Comfrim password while registration

    def validate(self, attrs):
        password =  attrs.get('password')
        password2 =  attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('Password and Confrim Password does not match')
        return attrs
    def create(self,validate_data):
        return RationUser.objects.create_user(**validate_data)

# User Login  Serializer

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = RationUser
        fields = ['email','password']
#user Get profile Serializer

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RationUser
        fields = ['id','email','name',]

# User Password Change Serializer
class UserChangePasswordSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, attrs):
    password = attrs.get('password')
    password2 = attrs.get('password2')
    user = self.context.get('user')
    if password != password2:
      raise serializers.ValidationError("Password and Confirm Password doesn't match")
    user.set_password(password)
    user.save()
    return attrs