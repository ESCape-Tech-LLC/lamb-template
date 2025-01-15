# Usage of template

## From local copy

```shell
django-admin startproject some_project \
  --template ../Lamb/lamb-template \
  --extension py,xml,yml,ipynb,sql,example-tpl \
  --exclude=__pycache__ \
  --exclude=.git \
  --exclude=.idea \
  --exclude=USAGE.md   
```

## From Public URL

```shell
django-admin startproject some_project --template https://github.com/ESCape-Tech-LLC/lamb-template/archive/refs/heads/master.zip --extension py,xml,yml,ipynb,sql,example-tpl --exclude=__pycache__ --exclude=.git --exclude=.idea  
```
