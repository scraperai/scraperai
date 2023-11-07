from fastapi import FastAPI

app = FastAPI()


def register(parent_app: FastAPI):
    parent_app.mount('/api', app)


@app.get('/')
def index():
    return {'status': 'success'}
