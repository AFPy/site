# AFPy.org

Site Web de l'AFPy.


## Tester localement

Un `make install` suivi d'un `make serve` suffit pour tester
localement sans article.

Si vous voulez des articles, lancez un `tar xjf posts.tar.bz2`
d'abord.

Si vous avez votre propre venv, un `FLASK_APP=afpy.py
FLASK_ENV=development flask run` vous suffira.


## Tester

```bash
pip install -e.[test]
make test  # ou make test VENV="$VIRTUAL_ENV" pour utiliser votre venv.
```


## Déployer

Pour publier il suffit de `git push`, une action github s'occupe de la mise en prod.
