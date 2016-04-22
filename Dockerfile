FROM praekeltfoundation/django-bootstrap
ENV DJANGO_SETTINGS_MODULE "seed_continuous_learning.settings"
RUN ./manage.py collectstatic --noinput
ENV APP_MODULE "seed_continuous_learning.wsgi:application"
