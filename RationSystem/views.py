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
  
class SentpasswordResetEmail(APIView):
    renderer_classes = [UserRenderer]
    def post(self,request,format=None):
        pass