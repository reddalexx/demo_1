import os
import redis
from celery import Celery, states, signals
from celery.result import AsyncResult

from .search import TripAdviserHotelsSearch


app = Celery(
    'fastapi_tasks',
    broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_BACKEND_URL', 'redis://localhost:6379/0'),
    result_extended=True,
)

r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
demo_task_results_cache_key = 'demo_task_results'


@signals.task_prerun.connect
def save_initial_state(task_id, task, *args, **kwargs):
    """
    Save initial state in AsyncResult - to have valid task AsyncResult at task start to provide in get_completed_tasks()
    """
    task.backend.store_result(task_id, None, states.PENDING, request=task.request)


@app.task(bind=True, name='Get Hotels Urls')
def get_hotels_urls(task, query: str, page: int):
    """
    Get hotel list page, extract hotel urls from that page (30 items), start subtasks to scrape details for each hotel
    """
    r.hset(demo_task_results_cache_key, task.request.id, 0)    # TODO: let's use len(initial_data) instead of 0
    _, hotels_initial_data = TripAdviserHotelsSearch().get_initial_hotels_data(query, page)
    for hotel_data in hotels_initial_data:
        parse_hotel_data.s(hotel_data).delay()


@app.task(name='Parse Hotel Data')
def parse_hotel_data(hotel_initial_data):
    """
    Parse individual hotel data from hotel details page
    """
    return TripAdviserHotelsSearch().seq_get_and_parse_html_page(hotel_initial_data)


def get_completed_tasks():
    """
    Get completed tasks - i.e. task progress of main task + child task stats.
    Return {"{parent_task_id}": {"overview": ..., "progress": int[0.100], "results": list[dict]}}
    """
    # TODO: make celery periodic task?
    ret = dict()
    for parent_task_id in r.hgetall(demo_task_results_cache_key):
        parent_task_id = parent_task_id.decode('utf-8') if isinstance(parent_task_id, bytes) else parent_task_id
        this_task_ret = dict()

        parent_task_result = AsyncResult(parent_task_id)
        child_task_results = parent_task_result.children
        this_task_results = [parent_task_result]

        this_task_ret['overview'] = {
            'master_task_status': parent_task_result.status,
        }
        child_task_statuses = []
        if child_task_results:
            this_task_results += child_task_results
            child_task_statuses = [i.status for i in child_task_results]
            this_task_ret['overview']['child_tasks_statuses'] = {
                states.SUCCESS: len([i for i in child_task_statuses if i == states.SUCCESS]),
                states.PENDING: len([i for i in child_task_statuses if i == states.PENDING]),
                states.FAILURE: len([i for i in child_task_statuses if i == states.FAILURE]),
                'TOTAL': len(child_task_statuses)
            }

        ready_states = [i in states.READY_STATES for i in child_task_statuses + [parent_task_result.status]]
        this_task_ret['progress'] = int(sum(ready_states) / len(ready_states) * 100)

        if all(ready_states):
            r.hdel(demo_task_results_cache_key, parent_task_id)
            this_task_ret['results'] = [i.result for i in child_task_results]

        ret[parent_task_id] = this_task_ret
    return ret
