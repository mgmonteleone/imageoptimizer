import multiprocessing

bind = ":5000"
workers = multiprocessing.cpu_count()  + 1