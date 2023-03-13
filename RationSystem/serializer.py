
from xml.dom import ValidationErr
from rest_framework import serializers
from RationSystem.models import RationUser
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import face_recognition


# user creation Serializer

class UserRegistrationSerializer(serializers.ModelSerializer):
    #we are writing this because we need comfrim password field in outr Ragistration Request
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    face_image = serializers.ImageField()
    class Meta:
        model = RationUser
        fields =['email','rationId','name','tc','password','password2','face_image']

        extra_kwargs={
            'password':{'write_only':True }
        }

    # Validation Password and Comfrim password while registration

    def validate(self, attrs):
        password =  attrs.get('password')
        password2 =  attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError('Password and Confrim Password does not match')
        
        face_image = attrs.get('face_image')
        # Use face_recognition library to check if the image is a face image
        try:
            image = face_recognition.load_image_file(face_image)
            face_locations = face_recognition.face_locations(image)
            if len(face_locations) == 0:
                raise serializers.ValidationError('The uploaded image is not a face image')
        except:
            raise serializers.ValidationError('Failed to process the uploaded image')
        return attrs
    def create(self,validate_data):
        return RationUser.objects.create_user(**validate_data)
        

# User Login  Serializer

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    rationId =serializers.CharField(max_length=255)
    class Meta:
        model = RationUser
        fields = ['email','rationId','password']
#User face Authentication

class FaceAuthenticationSerializer(serializers.Serializer):
    face_image = serializers.ImageField()
    class Meta:
        model = RationUser
        fields = ['face_image']


    def validate(self, attrs):
        # Use face_recognition library to check if the image is a face image
        try:
            image = face_recognition.load_image_file(attrs['face_image'])
            face_encodings = face_recognition.face_encodings(image)
            face_locations = face_recognition.face_locations(image)
            if len(face_encodings and face_locations) == 0:
                raise serializers.ValidationError('The uploaded image is not a face image')
        except:
            raise serializers.ValidationError('Failed to process the uploaded image here face is not detected')
        return attrs


#user Get profile Serializer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RationUser
        fields = ['id','email','rationId','name',]

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

#user password reset

class SendPasswordResetEmailSerializer(serializers.Serializer):
  email = serializers.EmailField(max_length=255)
  class Meta:
    fields = ['email']

  def validate(self, attrs):
    email = attrs.get('email')
    if RationUser.objects.filter(email=email).exists():
      user = RationUser.objects.get(email = email)
      uid = urlsafe_base64_encode(force_bytes(RationUser.id))
      print('Encoded UID', uid)
      token = PasswordResetTokenGenerator().make_token(user)
      print('Password Reset Token', token)
      link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token
      print('Password Reset Link', link)
      # Send EMail
      body = 'Click Following Link to Reset Your Password '+link
      data = {
        'subject':'Reset Your Password',
        'body':body,
        'to_email':RationUser.email
      }
      # Util.send_email(data)
      return attrs
    else:
      raise serializers.ValidationError('You are not a Registered User')
    
class UserPasswordResetSerializer(serializers.Serializer):
  password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
  class Meta:
    fields = ['password', 'password2']

  def validate(self, attrs):
    try:
      password = attrs.get('password')
      password2 = attrs.get('password2')
      uid = self.context.get('uid')
      token = self.context.get('token')
      if password != password2:
        raise serializers.ValidationError("Password and Confirm Password doesn't match")
      id = smart_str(urlsafe_base64_decode(uid))
      user = RationUser.objects.get(id=id)
      if not PasswordResetTokenGenerator().check_token(user, token):
        raise serializers.ValidationError('Token is not Valid or Expired')
      user.set_password(password)
      user.save()
      return attrs
    except DjangoUnicodeDecodeError as identifier:
      PasswordResetTokenGenerator().check_token(user, token)
      raise serializers.ValidationError('Token is not Valid or Expired')