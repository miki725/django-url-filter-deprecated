Comparison
==========

Filter outline
--------------

Before comparing the differences between this and other similar libraries,
the following is a quick summary of how Django URL Filter filters
a given queryset:

.. _outline_step1:

1. FilterSet class is created (``class FooFS(FilterSet): ...``).
   During its creation, its metaclass constructs filters for
   all fields for the model defined in the ``Meta.model``.
   If any custom filters are defined, the auto-generated
   filters are replaced the by the custom filters.

.. _outline_step2:

2. FilterSet is initialized to filer a specific queryset
   (``FooFS(data, qs)``).

.. _outline_step3:

3. ``FooFS``'s ``qs`` attribute is accessed to get the filtered
   queryset.

.. _outline_step4:

4. ``FooFS`` loops through all of the data (``QueryDict``) keys
   and matches if any of the keys start with filter keys.
   If there is a match, the matched filter is used to
   filter the queryset. Filterset passes the queryset,
   ``QueryDict`` key and corresponding value to the filter.

.. _outline_step5:

5. Filter validates the ``QueryDict`` key by using a specialized
   form field. The field splits the key into 3 pieces of
   information - the key, lookup type (e.g. ``exact``, ``contains``)
   and negation (whether filter in inclusive or exclusive -
   ``qs.filter()`` vs ``qs.exclude()``).

.. _outline_step6:

6. If the key is validated and parsed successfully by the key field,
   filter then validates the corresponding ``QueryDict``'s value.
   It validates it by figuring out which form field should
   be used to validate the value. For example if the filter
   is for ``models.CharField``, it will use ``forms.CharField``
   field to validate the value. However in some cases the form
   field will be overwritten depending either on the model field
   of the filter or the lookup type. For example, for
   ``models.FileField``, ``forms.CharField`` will be used
   since you don't want to filter by files but rather by the
   file path. Another example is for ``models.IntegerField``
   with lookup type of ``isnull``, ``forms.BooleanField``
   will be used instead of ``forms.IntegerField``.

.. _outline_step7:

7. If the value is validated by the form field, filter then
   filters the queryset by either using filter or exclude
   (as determined by the negation parameter while parsing the
   ``QueryDict`` key). For performance reasons, filter does
   filter the queryset directly but rather returns ``kwargs``
   dictionary which can be passed to ``filter`` or ``exclude``.
   This allows the ``FooFS`` to apply a filter for all filters
   in one shot instead of duplicating the queryset many times.

.. _outline_step8:

8. Filterset returns the final filtered queryset by calling
   ``qs.filter()`` and/or ``qs.exclude()`` once with the
   appropriate ``kwargs``.

Advantages
----------

problems
~~~~~~~~

In order to understand the advantages of this approach, it is
probably a good idea to understand some of the disadvantages
of similar libraries (mostly ``django-filters``). It is an excellent
library for some uses however after using it myself on a couple of projects,
I had to fight it to fit my project requirements and some things I could not get
to work at all due to some of the design choices of the library.

The biggest constraint of ``django-filters`` I found was that it creates
a form for the whole ``QueryDict`` which it validates at once and then
filters content according to the ``cleaned_data``. I like this for
performance because it only needs to construct one form class
instance to validate everything. The disadvantage is that the form
fields then have to be predefined. For example for the following
FilterSet::

    class FooFilter(django_filters.FilterSet):
        price = NumberFilter(...)
        name = CharFilter(...)
        class Meta:
            model = Foo

the constructed form will be very similar to::

    class FooForm(forms.Form):
        price = LookupTypeField(fields=( # based of MultiValueField
            DecimalField(...),           # value
            ChoiceField(...),            # lookup_type
        ))
        name = LookupTypeField(fields=(
            CharField(...),              # value
            ChoiceField(...),            # lookup_type
        ))

which will require the URL something like::

    GET /foo/?price_0=1&price_1=exact&name_0=bar&name_1=contains

The problem with this is that if for example you need to use lookup_type
of ``isnull`` for the ``price``, you might want the following url::

    GET /foo/?price_0=false&price_1=isnull&name_0=bar&name_1=contains

but that will never validate because of the ``price_0=false`` will not pass the
``DecimalFilter`` form field.

The second problem I found with this is that each model field gets only one
form field (``LookupTypeField``). The following Django queryset filter
becomes impossible::

    qs.filter(price__gt=1.0, price__lt=2.0)

solutions
~~~~~~~~~

The first problem of having fixed form fields for validating input gets
solves because Django URL Filter does not use forms to validate the whole
``QueryDict`` at once. Instead since when it finds the filter for the
``QueryDict`` key (`step 4 <outline_step4_>`_), it passes all of the
information to the filter which depending on the model field and/or
lookup_type determines the form field to use to validate the
data (`step 6 <outline_step6_>`_). This allows for::

    GET /foo/?price__exact=1.0
    or
    GET /foo/?price__isnull=false     # not decimal but boolean data-type

    GET /foo/?created__gt=2013-11-06
    or
    GET /foo/?created__year=2013      # not datetime but integer data-type

In order words, lookup type is considered before validating the data.

The second problem of allowing multiple filters for the same model fields
is solved by how FilterSet matches a filter to the ``QueryDict``'s key.
Since it loops through the ``QueryDict`` and finds filters on the go,
it does not care that the same field key might be used more than once.
This allows for::

    GET /foo/?price__gt=1.0&price__lt=2.0
