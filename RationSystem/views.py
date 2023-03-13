from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from RationSystem.serializer import * 
# from django.contrib.auth import authenticate,get_user_model
from RationSystem.customAuthenticationBackend import RationUserAuthenticationBackend
from  RationSystem.renderer import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from deepface import DeepFace
# Create your views here.




#generate Token Manually

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

#create User Registration

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception = True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({
                'token':token,
                'msg':"User Registration Successful"
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
# create User Login 
# class UserLoginView(APIView):
#     renderer_classes =  [UserRenderer]
#     def post(self,request,format=None):
#         serializer = UserLoginSerializer(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             email = serializer.data.get('email')
#             rationId = serializer.data.get('rationId')
#             password =  serializer.data.get('password')
#             user = authenticate(request,email=email,rationId=rationId,password=password)
            
#             if user is not None:
#                  token = get_tokens_for_user(user)
#                  return Response({
#                      'token':token,
#                         "msg":"Login Successful"
#                         },
#                         status=status.HTTP_200_OK
#                         )
#             else:
#                 return Response({
#                     "errors":{
#                         'none_field_errors':
#                                     ['email or password is not vaild ']
#                         }
#                    },status=status.HTTP_404_NOT_FOUND)
            
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            rationId = serializer.data.get('rationId')
            password = serializer.data.get('password')
            user = RationUserAuthenticationBackend.authenticate(self,request,
                                                                email=email,
                                                                rationId=rationId,
                                                                password=password)
            print(user)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({
                    'token': token,
                    "msg": "Login Successful"
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "errors": {
                        'none_field_errors':
                            ['email or rationId or password is not valid']
                    }
                }, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class FaceAuthenticationView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        serializer = FaceAuthenticationSerializer(data=request.data)
        if serializer.is_valid():
            face_image = serializer.validated_data['face_image']
            # Load the user from the database based on the email or ration ID
            email_or_ration_id = request.user.rationId if request.user.is_authenticated else request.session.get('email_or_ration_id')
            try:
                user = RationUser.objects.get(email=email_or_ration_id) if '@' in email_or_ration_id else RationUser.objects.get(rationId=email_or_ration_id)
            except RationUser.DoesNotExist:
                return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            # Use face_recognition library to check if the uploaded image matches the user's face
            try:
                user_image = face_recognition.load_image_file(user.face_image.path)
                user_face_encoding = face_recognition.face_encodings(user_image)[0]
                uploaded_image = face_recognition.load_image_file(face_image)
                uploaded_face_encoding = face_recognition.face_encodings(uploaded_image)[0]
                face_distances = face_recognition.face_distance([user_face_encoding], uploaded_face_encoding)
                face_match = face_distances[0] < 0.6
                # perform face recognition
                result = DeepFace.verify(user_image, uploaded_image, model_name="Facenet")
                if not face_match or not result["verified"]:
                    return Response({'detail': 'Face not matched @@@@@@ authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({'detail': 'Failed to process the uploaded image or it is not a face'}, status=status.HTTP_400_BAD_REQUEST)

            # Authenticate the user if not already authenticated
            if not request.user.is_authenticated:
                user = authenticate(request, email=email_or_ration_id, password=request.session.get('password'))
                if user is None:
                    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


            return Response({
                    'detail': 'Face authentication succeeded',
                    'token':get_tokens_for_user(user)
                }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self,request,format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)
  
class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)


class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)
