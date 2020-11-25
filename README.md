# AFPy.org

Site Web de l'AFPy.


## Tester localement

Commencez par un `make install`

Ensuite, `mv .env.template .env` en remplacant les valeurs nécéssaires

Puis un `make serve` suffit pour testerlocalement sans article.

Si vous voulez des articles, lancez un `tar xjf posts.tar.bz2`
d'abord, puis un `python xml2sql.py` ce qui remplira la DB

## Tester

```bash
make test
```

## Déployer

Pour publier il suffit de `git push`, une action github s'occupe de la mise en prod.
