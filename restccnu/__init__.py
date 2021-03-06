# coding: utf-8

import redis
from flask import Flask, render_template, request
from flask_zero import Qiniu
from celery import Celery
from config import config


qiniu = Qiniu()
# 静态资源存储
# rds = redis.StrictRedis(host='localhost', port=6384, db=0)
rds = redis.StrictRedis(host='redis1', port=6384, db=0)
"""
6384rds~>
    1. banners: banner [{'filename':'url'}]
    2. calendars: calendar [{'filename': 'size'}]
    3. apps: ccnubox version
    4. patchs: ccnubox patchs version
    5. products: muxi products { "products":
        [
            {
                "name": "学而",
                "icon": "",
                "url": "https://xueer.muxixyz.com",
                "intro": "华师课程经验挖掘机",
            },
            {....}
        ],
        "update": "2016-08-22"
    }
"""
board = redis.StrictRedis(host='redis2', port=6381, db=0)
"""
    1. board_list: 通知公告缓存 []
"""


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    qiniu.init_app(app)

    from apis import api
    app.register_blueprint(api, url_prefix='/api')

    return app


app = create_app()

@app.route('/')
def index():
    # if 'iphone' in str(request.user_agent).lower():
    #    return render_template('ios.html')
    return render_template('index.html')

@app.route('/info/')
def info():
    return render_template('letter.html')

@app.route('/qa/')
def qa():
    return render_template('qaindex.html')

@app.route('/h5/')
def h5():
    platform = request.user_agent.platform
    if platform in ["android", "iphone", "ipad"]:
        return render_template('index_m.html')
    else:
        return render_template('index_d.html')


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
