tasks
===

__tasks.py__ is a simple and fast task queue for executing multiple tasks in parallel. All you need to do is specify the task as a simple function that takes an argument and you get instant parallelism.

Based on eventlet, multiprocessing and redis.

It is ideal for executing multiple network bound tasks in parallel from a single node, without going through the pain of setting up a map reduce cluster. It uses both processes and green threads to extract the maximum out of a single node setup.

Installation
-----------

1. Install redis and start the server, **tasks** uses redis for queueing jobs. If you already have a redis server setup, call `tasks.set_redis` and pass a redis connection object with a different database/namespace from what you normally use in your application. 

2. Install the redis-py and eventlet libraries.
	
    `pip install redis eventlet`

3. Install tasks or copy this package to your source code.

    `pip install tasks-py`

Usage
-----
Import `tasks` and call eventlet's monkey patch function in the first line of your module. Call `tasks.set_func` to register your function. This function will be receiving a string as an argument and its return value will be ignored. To indicate failure of the task, raise an error or exception within the function. Call `tasks.main()` to get the interactive command line options.  	

    import eventlet
    eventlet.monkey_patch()
    import tasks
    
    from urllib2 import urlopen
    
    def fetch(url):
    	f = open('/tmp/download', 'w')
    	body = urlopen(url).read()
    	f.write(body)
    	f.close()
    	
    tasks.set_func(fetch)
    tasks.main()
    
Now to add jobs, create a file with one argument per line and use this command.

`$ python yourfile.py add <list_of_jobs.txt>`

To start (or restart) the job processing (do this in a **screen** session or close the input stream):

`$ python yourfile.py run`

**tasks** has resume support, so it will start where you left off the last time.

To view the current status while it is running: 

`$ python yourfile.py status`

Once you are done, you can clear the logs and the completed tasks by calling reset.

`$ python yourfile.py reset`

See the code or the test.py file for more information. Feel free to fork and modify this.

----

**Author** : Vivek Narayanan <<vivek_n@me.com>>

**License** : BSD

(C) Vivek Narayanan (2014)


