Django URL filter
=================

.. image:: https://travis-ci.org/miki725/django-url-filter.png?branch=develop
    :target: https://travis-ci.org/miki725/django-url-filter
    :alt: Build Status

.. image:: https://d2weczhvl823v0.cloudfront.net/miki725/django-url-filter/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free

Generic Django filtering system with easy URL interface.
Useful for APIs such as `Django REST <http://django-rest-framework.org/>`_.

Overview
--------

The main goal of Django URL Filter is to provide an easy URL interface
for filtering querysets. It allows the user to safely filter by model
attributes and also allows to specify the lookup type for each filter
(very much like Django's filtering system). For example the following
will retrieve all items where the id is ``5`` and title contains ``"foo"``::

    GET http://example.com/listview/?id=5&title__contains=foo

In addition to basic lookup types, Django URL Filter allows to
use more sophisticated filters such as ``in`` or ``year``.
For example::

    GET http://example.com/listview/?id__in=1,2,3&created__year=2013

Documentation
-------------

Documentation can be found at
`Read The Docs <http://django-url-filter.readthedocs.org/>`_.

Requirements
------------

* Python (2.6, 2.7 and 3.3)
* Django 1+ (no specific Django features are used so should even
  work even on <1.3)

Installing
----------

Since this package is still in development, no stable version has been
uploaded to PYPI yet. You can however install it as a
`developer <http://github.com/miki725/django-url-filter/archive/develop.tar.gz#egg=django_url_filter-dev>`_
version::

    $ pip install django-url-filter==dev

Example
-------

Using Django URL Filter with Django REST is just a matter of changing
the filter backend::

    from django.contrib.auth.models import User
    from url_filter.backend import URLDjangoFilterBackend

    class ListView(generics.ListAPIView):
        model = User
        filter_backends = (URLDjangoFilterBackend,)
        filter_fields = ('id', 'email', 'is_active', 'date_joined')

Assuming the previous view is enabled via ``/users/`` url, the following
queries become possible::

    GET /users/?id=5                          # id is equal to 5
    GET /users/?id__in=1,2,3                  # id either 1, 2 or 3
    GET /users/?id__!exact=1                  # id not 1
    GET /users/?is_active=true                # active users
    GET /users/?is_active__isnull=false       # active state is defined
    GET /users/?date_joined__gte=2013-11-06   # joined on or after Nov 11, 2013
                                              # (Django 1.6 release date)
    GET /users/?date_joined__range=2013-02-26,2013-11-06
                                              # joined between Feb 26, 2013 and Nov 11, 2013
                                              # (Django 1.5 and 1.6 release dates)

Credits
-------

Current maintainers:

    * Miroslav Shubernetskiy - miroslav@miki725.com

Inspiration libs:

* `django-filters <https://github.com/alex/django-filter>`_ was a strong inspiration
  for creating this library so huge thanks for all the smart people involved there.
  I did use it for a while however some features I wanted ``django-filters`` to
  have were either hard to accomplish or required monkey patching (e.g. the URL
  interface) or were not possible at all due to design constrains of the library.
  For more details about the differences you can look in the docs.
* `django-rest-framework-chain <https://github.com/philipn/django-rest-framework-chain>`_
  also served as inspiration. Even though this library enables better URL interface,
  it still relies on ``django-filters`` hence similar constrains apply.

Future
------

Some of the things on the todo roadmap

* **Relation filters**

  Currently the library only works with non-relation model fields which means you
  can't filter against table joins like Django querysets allow.

