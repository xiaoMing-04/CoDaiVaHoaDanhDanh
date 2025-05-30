"""
URL configuration for GameArt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import homepage.urls
import games.urls
import thanks.urls
import users.urls
import cart.urls
import search.urls
import transactions.urls
import keys.urls
import game_features.urls
import track.urls
import blog.urls
import wishlist.urls
import notification.urls
import list.urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(homepage.urls)),
    path('', include(games.urls)),
    path('thanks/', include(thanks.urls)),
    path('', include(users.urls)),
    path('', include(cart.urls)),
    path('', include(search.urls)),
    path('', include(transactions.urls)),
    path('', include(keys.urls)),
    path('', include(game_features.urls)),
    path('', include(track.urls)),
    path('', include(blog.urls)),
    path('', include(wishlist.urls)),
    path('', include(notification.urls)),
    path('', include(list.urls)),
    path('', include('livestream.urls')),
    path('', include('spotifyplayer.urls'))
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)