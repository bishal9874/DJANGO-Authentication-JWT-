from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.utils.safestring import mark_safe

# Create your models here.
#custom user Manager
class MyUserManager(BaseUserManager):
    def create_user(self, email,rationId ,name,tc,face_image,password=None,password2=None):
        """
        Creates and saves a User with the given email, name, tc and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not face_image:
            raise ValueError("Users must have an Face ID ")

        user = self.model(
            email=self.normalize_email(email),
            rationId = rationId,
            name = name,
            tc=tc,
            face_image = face_image
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
        

    def create_superuser(self, email,rationId ,name,tc,face_image, password=None):
        """
        Creates and saves a superuser with the given email, name, tc and password.
        """
        
        user = self.create_user(
            email,
            rationId = rationId,
            password=password,
            name=name,
            tc=tc,
            face_image=face_image
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

#Custom user Model

class RationUser(AbstractBaseUser):

    def user_dir_path(instance, filename):
        filename = f'{instance.rationId}.jpg'
        return 'user_{0}/{1}'.format(instance.rationId, filename)
    
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    rationId = models.CharField(max_length=255,unique=True)
    name = models.CharField(max_length=200)
    tc = models.BooleanField()
    face_image = models.FileField(upload_to=user_dir_path)
    # date_of_birth = models.DateField()
    
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at =  models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  
    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name','rationId','tc','face_image']

    

    def __str__(self):
        return self.email
    
    def user_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.face_image.url))
    user_photo.allow_tags = True
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    


