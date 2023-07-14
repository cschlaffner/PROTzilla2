import multiprocessing
import threading
import time

threads = {}


def write_to_csv(item, path, *args, **kwargs):
    item.to_csv(path, *args, **kwargs)


def async_to_csv(item, path, *args, **kwargs):
    p = threading.Thread(
        target=write_to_csv,
        args=(item, path, *args),
        kwargs=kwargs,
    )
    p.start()
    threads[path] = p
    remove_finished_processes()



def remove_finished_processes():
    finished = list()
    for path in threads.keys():
        if not threads[path].is_alive():
            finished.append(path)
    for path in finished:
        threads[path].join()
        del threads[path]


def wait_for(path_to_wait_for):
    remove_finished_processes()
    for path, process in threads.items():
        if path_to_wait_for == path or path_to_wait_for in path.parents:
            # print(f"waiting: {path_to_wait_for=}\n {path=}")
            process.join()


def kill_all_with_path(kill_path):
    remove_finished_processes()
    for path, process in threads.items():
        if kill_path == path or kill_path in path.parents:
            # print(f"killing: {kill_path=}\n {path=}")
            process.join()
    time.sleep(0.3)
