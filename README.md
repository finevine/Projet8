# Purbeurre

Purbeurre is a class project: it's a website that aims to find and replace unhealthy food in real life by better substitute.

This project is based on:
- [Django](https://docs.djangoproject.com/fr/3.0/)
- [Bootstrap](https://getbootstrap.com/docs/4.0/getting-started/introduction/)
- [Creative Bootstrap theme](https://github.com/BlackrockDigital/startbootstrap-creative)

## Requirements 

Requirements are given in a pdf. The site should look like that:
![esquisses 1 et 2](/project/img/esquisses-1-2.jpg)
![esquisses 3 et 4](/project/img/esquisses-3-4.jpg)

## Theme customization

`Node.js` is installed to customize SASS file of the Bootstrap theme. Then [Bootstrap variables](https://github.com/twbs/bootstrap-sass/blob/master/assets/stylesheets/bootstrap/_variables.scss) are customized.

creative.min.css is then compiled using `npm start`

## Tests

Tests can be launched in the `pipenv shell`

```python
./manage.py test --verbosity=2
```

Coverage is studied by 
```python
coverage run --source='.' manage.py test myapp
````

and then `coverage report`

## INIT et UPDATE

importer 90 produits par categories
Avec une limite de 9000 produits en tout

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)