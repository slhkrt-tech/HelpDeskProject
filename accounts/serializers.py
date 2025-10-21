# accounts/serializers.py
# ================================================================================
# Django REST Framework Serializers
# API endpoint'ler için veri serileştirme ve validasyon
# ================================================================================

from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()  # CustomUser modelini dinamik al

class LoginSerializer(serializers.Serializer):
    """
    Kullanıcı giriş API'si için serializer
    Username/password validasyonu ve kimlik doğrulama
    """
    username = serializers.CharField(max_length=150, help_text="Kullanıcı adı")
    password = serializers.CharField(write_only=True, help_text="Kullanıcı şifresi")

    def validate(self, data):
        """
        Login bilgilerini doğrula ve kullanıcıyı authenticate et
        """
        username = data.get('username')
        password = data.get('password')

        if username and password:
            # Kullanıcı kimlik doğrulama
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('Kullanıcı hesabı devre dışı.')
            else:
                raise serializers.ValidationError('Geçersiz kullanıcı adı veya şifre.')
        else:
            raise serializers.ValidationError('Kullanıcı adı ve şifre gerekli.')
        
        return data

class UserSerializer(serializers.ModelSerializer):
    """
    Kullanıcı bilgileri için serializer
    API response'larında kullanıcı bilgilerini döndürür
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active']
        read_only_fields = ['id', 'is_staff']  # Sadece okunabilir alanlar