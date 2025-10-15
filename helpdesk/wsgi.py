#bu dosya, Django uygulamanızın bir WSGI sunucusu tarafından çalıştırılabilmesi için gerekli başlangıç noktasıdır
#django’nun synchronous (normal) sunucularla çalışmasını sağlayan standart

import os #ortam değişkenlerini yönetmek için kullanılır.

from django.core.wsgi import get_wsgi_application #django uygulamasını WSGI uyumlu callable olarak alır

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings') #django’ya hangi ayar dosyasını (settings.py) kullanacağını söyler, boşsa helpdesk settings default döner

application = get_wsgi_application() #WSGI sunucusu tarafından kullanılacak ana giriş noktasıdır
                                     #sunucu, gelen HTTP isteklerini bu callable aracılığıyla Django uygulamasına iletir