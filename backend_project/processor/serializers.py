from rest_framework import serializers
from .models import YourModel  # yahan apne model ka naam use karo

class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'  # ya ['field1', 'field2'] jaise specific fields bhi de sakte ho
