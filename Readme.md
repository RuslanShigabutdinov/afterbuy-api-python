# Afterbuy API

## How to run

###
```bash 
pip install -r requirements.txt 
```

### 2 run celery
```
celery -A src.libs.celery_app worker -l info -P gevent
```

### run flower 

```
celery -A src.libs.celery_app flower --port=5555
```
