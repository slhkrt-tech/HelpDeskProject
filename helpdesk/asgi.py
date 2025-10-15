#bu dosya, Django uygulamanızın bir ASGI sunucusu tarafından çalıştırılabilmesi için gerekli başlangıç noktasıdır
#django’nun asenkron sunucularla çalışmasını sağlayan standart

import os #modülü, ortam değişkenlerini yönetmek için kullanılır

from django.core.asgi import get_asgi_application #django uygulamasının ASGI uyumlu bir callable (çağrılabilir obje) olarak kullanılmasını sağlar

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings') #django’ya hangi ayar dosyasını (settings.py) kullanacağını söyler, boşsa helpdesk settings default döner

application = get_asgi_application() #application değişkeni, ASGI sunucusu tarafından kullanılacak ana giriş noktasıdır
                                     #bu değişken sayesinde sunucu, gelen HTTP veya WebSocket isteklerini Django uygulamasına iletebilir