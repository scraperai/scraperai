# Scraper AI 

## Backend

### Development startup
Server:
```
uvicorn main:app --reload
```
Taskiq:
```
taskiq worker tasks:broker
```

### Database
Database initialization:
```
aerich init -t settings.TORTOISE_ORM
aerich init-db
```

Migraion:
```
aerich migrate
aerich upgrade
```
