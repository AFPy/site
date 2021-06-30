# AFPy.org

Site Web de l'AFPy.


## Tester localement

Commencez par un `make install`

Ensuite, `mv .env.template .env` en remplacant les valeurs
nécéssaires.

Créez le répertoire des images: `images` à la racine du projet (ou
ailleurs, configuré via `IMAGE_PATHS` dans le `.env`).

Puis un `make serve` suffit pour tester localement sans article.

Si vous voulez des articles, lancez un `tar xjf posts.tar.bz2`
d'abord, puis un `python xml2sql.py` ce qui remplira la DB

/!\ the default admin user is `admin:password

## Tester

```bash
make test
```

## Déployer

Pour publier il suffit de `git push`, une action github s'occupe de la mise en prod.
