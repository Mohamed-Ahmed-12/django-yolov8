from django.db import models
from django.core.exceptions import ValidationError
import os
# Create your models here.
def dynamic_path(instance, filename):
    extension = instance.file.name.split('.')[-1]
    if extension in ['jpg', 'jpeg', 'png', 'gif']:
        return f"vehicle/images/{instance.file}/{filename}"
    elif extension in ['mp4', 'mov', 'avi', 'wmv','webm']:
        return f"vehicle/videos/{instance.file}/{filename}"
    
def validate_file_extension(value):
    valid_extensions = ['.png', '.jpg', '.jpeg','.mp4','.mov','.avi','.wmv','.webm']
    file_extension = os.path.splitext(value.name)[1]
    if file_extension not in valid_extensions:
        raise ValidationError('Only png , jpg , jpeg, mp4 , mov , avi , wmv and webm files are allowed.')  
      
'''def validate_image_size(value):
    if value.size > 10485760:  # 10 MB
        raise ValidationError('File size cannot exceed 10 MB.')    
 '''   
class Vehicle(models.Model):
    file = models.FileField(verbose_name='',upload_to=dynamic_path , blank=False , null=False ,validators=[validate_file_extension])
    def __str__(self):
        return f"{self.id}"



'''
class Vehicle(models.Model):
    CLASS_CHOICES = [
        ("car", "Car"),
        ("motorbike", "Motorbike"),
        ("truck", "Truck"),
        ("van", "Van"),
        ("bus", "Bus"),
    ]
    COLOR_CHOICES = [
        ("red", "Red"),
        ("green", "Green"),
        ("blue", "Blue"),
        ("yellow", "Yellow"),
        ("orange", "Orange"),
        ("white", "White"),
        ("gray", "Grey"),
        ("black", "Black"),
        ("purple", "Purple"),
    ]
    BRAND_CHOICES = [
        # Audi, Chevrolet, Dodge, GMC, Honda, Hyundai, Jeep, Mazda, Mercedes, Mitsubishi, Nissan, Toyota, Volkswagen, bmw, dodge, ford, kia, suzuki, volvo
        ("Audi", "Audi"),
        ("Chevrolet", "Chevrolet"),
        ("Dodge", "Dodge"),
        ("GMC", "GMC"),
        ("Honda", "Honda"),
        ("Hyundai", "Hyundai"),
        ("Jeep", "Jeep"),
        ("Mazda", "Mazda"),
        ("Mercedes", "Mercedes Benz"),
        ("Mitsubishi", "Mitsubishi"),
        ("Nissan", "Nissan"),
        ("Toyota", "Toyota"),
        ("Volkswagen", "Volkswagen"),
        ("bmw", "BMW"),
        ("Ford", "Ford"),
        ("kia", "KIA"),
        ("suzuki", "Suzuki"),
        ("volvo", "Volvo"),
    ]
    STATUS_CHOICES = [
        ('damaged',"Damaged"),
        ('not-damaged',"Not Damaged")
    ]
    name = models.CharField(
        verbose_name="Class", choices=CLASS_CHOICES, max_length=20, blank=True
    )
    brand = models.CharField(verbose_name="Brand", choices=BRAND_CHOICES ,max_length=20, blank=True)
    color = models.CharField(
        verbose_name="Color", choices=COLOR_CHOICES, max_length=20, blank=True
    )
    status = models.CharField(verbose_name="Status", choices=STATUS_CHOICES ,max_length=20, blank=True)
    speed = models.FloatField(verbose_name="Speed", blank=True , null=True)
    file = models.FileField(
        verbose_name="Image Or Video", upload_to='vehicle/'
    )
    platenumber = models.ImageField(
        verbose_name="Plate Number",
        upload_to='plate/',
        blank=True,
    )

    def __str__(self):
        return f"{self.id}"
'''


"""
Choice field
list of tuples[(x,y),(),....], where the first element of each tuple is the value to be submitted and the second element is the human-readable label to be displayed to the user.
"""
