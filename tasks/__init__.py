import multiprocessing
import logging
import redis
import eventlet
import sys
import os

LOG_FORMAT = "%(asctime)s - %(processName)s - %(levelname)s - %(message)s"
LOG_FILE = "logfile"

def setup_logger(logFormat, logFileName):
    logger = multiprocessing.get_logger()
    logHandler = logging.FileHandler(logFileName, mode = 'a')
    logHandler.setFormatter(logging.Formatter(logFormat))
    logger.addHandler(logHandler)
    logger.setLevel(logging.DEBUG)
    return logger

logger = setup_logger(LOG_FORMAT, LOG_FILE)

ns_jobs = "jobs"
ns_in_progress = "in_progress"
ns_completed = "completed"

db = redis.Redis() # Edit this to point to your Redis instance

func = None

def set_func(_func):
    global func
    func = _func

def set_redis(rdb):
    global db
    db = rdb

def add_jobs(file_name):
    keys = [line.strip() for line in open(file_name)]
    if len(keys):
        db.sadd(*keys)

def sync_jobs():
    in_progress = db.smembers(ns_in_progress)
    if len(in_progress) > 0:
        db.sadd(ns_jobs, *in_progress)
    db.delete(ns_in_progress)

def print_status():
    njobs, nprog, ncomp = map(db.scard, [ns_jobs, ns_in_progress, ns_completed])
    print "jobs\n total: %d\n completed: %d\n in progress: %d" % ((nprog + njobs + ncomp), ncomp, nprog)

def divide_args(args, num):
    return [args[i:i+num] for i in xrange(0, len(args), num)]

#func will be your function, raise an error inside it to indicate failure and don't catch errors
def template_func(arg):
    try:
        db.srem(ns_jobs, arg)
        if db.sismember(ns_completed, arg):
            return
        db.sadd(ns_in_progress, arg)
        func(arg)
    except Exception as e:
        logger.error("Error with %s" % arg, exc_info=True)
        return False
    db.srem(ns_in_progress, arg)
    db.sadd(ns_completed, arg)
    return True

batch_size = 10000
num_procs = 2 * multiprocessing.cpu_count()
green_threads = 10

def green_func(chunk):
    pool = eventlet.GreenPool(green_threads)
    list(pool.imap(template_func, chunk))

def loop():
    while True:
        jobs = db.srandmember(ns_jobs, batch_size)
        pool = multiprocessing.Pool(num_procs)
        pool.map(green_func, divide_args(jobs, green_threads))
        if len(jobs) < batch_size:
            break
    sync_jobs()
    print_status()

def help():
    print "Usage: python %s {add <file_name>|run|status|reset}" % sys.argv[0]
    print "\n      add -> add a list of jobs from a file"
    print "      run -> start processing the jobs (with resume support)"
    print "      status -> show the current status of jobs in progress"
    print "      reset -> reset all jobs and logs"

def main():
    argc = len(sys.argv)

    if (argc < 2):
        help()
        return

    cmd = sys.argv[1]

    if cmd == "add" and argc == 3:
        add_jobs(sys.argv[2])
    elif cmd == "run":
        loop()
    elif cmd == "status":
        print_status()
    elif cmd == "reset":
        db.delete(ns_completed, ns_jobs, ns_in_progress)
        os.unlink(LOG_FILE)
    else:
        help()
