# wt-django-templatetags
[![Pytest](https://github.com/ian-wt/wt-django-templatetags/actions/workflows/pytest.yaml/badge.svg)](https://github.com/ian-wt/wt-django-templatetags/actions/workflows/pytest.yaml)
[![codecov](https://codecov.io/gh/ian-wt/wt-django-templatetags/graph/badge.svg?token=9MHTDPGG1N)](https://codecov.io/gh/ian-wt/wt-django-templatetags)

Useful templatetags for Django projects.

## Installation
Install from PyPi:
```shell
pip install wt-django-templatetags
```

Install from GitHub:

To install the development branch from GitHub:
```shell
pip install "wt-django-templatetags @ git+https://github.com/ian-wt/wt-django-templatetags.git"
```

Once installed, add `wt_templatetags` to `INSTALLED_APPS` in your settings module.

```python
INSTALLED_APPS = [
    # other packages
    'wt_templatetags',
]
```

Alternatively, you could register a particular module of templatetags directly in your
`TEMPLATES` setting.

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
            ],
            'libraries': {
                'pagination_tags': 'wt_templatetags.templatetags.pagination_tags',
            }
        },
    },
]
```
This is most useful when you're only interested in using a limited set
of modules from the broader project and that's unlikely to change. 
For simplicity, I recommend using the `INSTALLED_APPS` approach rather 
than selectively registering modules.

## Use
### Pagination Tags
To use the `pagination_tags` templatetags library in your project,
first load the tags with `{% load pagination_tags %}`.

To use the `relative_url` tag, you need to pass to the tag a page index.
This could be a number or the string `'last'` if the index is in the final
position of the paginated `QuerySet`. The tag additionally accepts optional
arguments for `field_name` and `urlencode`.

Most often, you'll leave the `field_name` parameter alone since the default
value of `'page'` is fairly semantic as it is. However, this value can be
overridden in your views so make sure your views and the `field_name` 
are consistent.

Last, the `urlencode` parameter is used when a query string may be present.
If your view won't ever handle a query string, then you can leave the default
value of `None` alone.

#### Example
```html
{% extends 'base.html' %}
{% load pagination_tags %}
<h1>Hello World!</h1>
<a href="{% relative_url page_obj.next_page_number %}">Next Page</a>
```
To extend this example further we can supply values to override the defaults:
```html
{% extends 'base.html' %}
{% load pagination_tags %}
<h1>Hello World!</h1>
<a href="{% relative_url page_obj.next_page_number 'page' request.GET.urlencode %}">Next Page</a>
```
