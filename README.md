# Inmobiliario

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Enfoques

3 enfoques:

- Modelo se sirve desde el frontend y se guardan respuestas en el backend.
- Modelo corre en backend para consumirse por distintos clientes.
- Modelo corre local por privacidad.

## Modelo en frontend

El frontend se encuentra dentro del gpt-assistant folder. Está en Nextjs.

#### Beneficios

- Menor latencia al no hacer request a un servidor externo.

#### Desventajas

- En la medida en que la aplicacón va creciento, línea difusa entre qué equipo se encarga del modelo y quien de la aplicación y la interfaz del usuario.
- Machine Learning Engineers usualmente no programan en javasript (o un framework como Nextjs).

![Frontend](./images/frontend.png 'opt title')

## Backend

#### Beneficios

- Línea clara entre el equipo de machine learning y frontend. MLE puede programar en python.

![backend](./images/backend.png 'opt title')

## Local

#### Beneficios

En caso de que se pretenda dar más privacidad lo cuál se convierte en desventaja si queremos reentrenar o mejorar nuestros modelos.

![pic alt](./images/local.png 'opt title')

### Django admin and DB

![pic alt](./images/admin.png 'opt title')

### Mejoras

Sin duda hay una lista de mejoras al demo:

- Framework de evaluación. Una de las partes más complicadas en modelos de lenguaje.
- Usar guardrials como un layer antes de enviar respuestas al usuario.
- Modelos de imágenes: quiero saber casas de este estilo, con xs características, dime el precio promedio.

#### Pre-commit

### Type checks

Running type checks with mypy:

    $ mypy inmobiliario

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest
