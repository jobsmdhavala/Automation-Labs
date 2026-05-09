#http://www.apache.org/licenses/LICENSE-2.0.txt
#
#
#Copyright 2016 Intel Corporation
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

import os
import threading
import subprocess
import fcntl

import time

from logger import log


def _non_block_read(output):
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.readline()
    except:
        return ""


class Binary(object):

    def __init__(self, url, location):
        super(Binary, self).__init__()
        self._url = url
        self._dir = location
        self._name = os.path.basename(url)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, u):
        self._url = u

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, loc):
        self._dir = loc

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, n):
        self._name = n

    def __str__(self):
        return self._name


class Plugin(Binary):

    def __init__(self, url, location, plg_type, version):
        super(Plugin, self).__init__(url, location)
        self._plg_type = plg_type
        self._version = version
        self.plg_name = os.path.basename(self.name.replace("-", os.sep))

    @property
    def plg_type(self):
        return self._plg_type

    @plg_type.setter
    def plg_type(self, t):
        self._plg_type = t

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, v):
        self._version = v

    def __str__(self):
        return ":".join([self.plg_type, self.plg_name, str(self.version)])


class Snapteld(Binary, threading.Thread):

    def __init__(self, url, location):
        super(Snapteld, self).__init__(url, location)
        self.stdout = None
        self.stderr = None
        self.errors = []
        self._stop = threading.Event()
        self._ready = threading.Event()
        self._process = None

    def run(self):
        cmd = '{} -t 0 -l 1 '.format(os.path.join(self.dir, self.name))
        log.debug("starting snapteld thread: {}".format(cmd))
        self._process = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while not self.stopped():
            out = _non_block_read(self._process.stderr)
            if "snapteld started" in out:
                self._ready.set()
                log.debug("snapteld is ready")
            if "error" in out:
                self.errors.append(out)
        if not self._process.poll():
            self._process.kill()
        log.debug("exiting snapteld thread")

    def stop(self):
        self._stop.set()
        self.join()

    def stopped(self):
        return self._stop.isSet()

    def wait(self, timeout=10):
        start = time.time()
        current = time.time()
        while not self._ready.isSet() and current - start < timeout:
            current = time.time()
            time.sleep(0.5)
        return current - start < timeout

    def kill(self):
        self._process.kill()
        self.stop()


class Snaptel(Binary):

    def __init__(self, url, location):
        Binary.__init__(self, url, location)
        self.errors = []

    def load_plugin(self, plugin):
        cmd = '{} plugin load {}'.format(os.path.join(self.dir, self.name), os.path.join(plugin.dir, plugin.name))
        log.debug("snaptel load plugin {}".format(cmd))
        out = self._start_process(cmd)
        log.debug("plugin loaded? {}".format("Plugin loaded" in out))
        return "Plugin loaded" in out

    def unload_plugin(self, plugin):
        cmd = '{} plugin unload {} {} {}'.format(os.path.join(self.dir, self.name), plugin.plg_type, plugin.plg_name, plugin.version)
        log.debug("snaptel unload plugin {}".format(cmd))
        out = self._start_process(cmd)
        log.debug("plugin unloaded? {}".format("Plugin unloaded" in out))
        return "Plugin unloaded" in out

    def list_plugins(self):
        cmd = '{} plugin list'.format(os.path.join(self.dir, self.name))
        log.debug("snaptel plugin list")
        plugins = self._start_process(cmd).split('\n')[1:-1]
        return plugins

    def create_task(self, task):
        cmd = '{} task create -t {}'.format(os.path.join(self.dir, self.name), task)
        log.debug("snaptel task create")
        out = self._start_process(cmd).split('\n')
        # sleeping for 10 seconds so the task can do some work
        time.sleep(10)
        if not len(out):
            return "" 
        log.debug("task created? {}".format(out[1] == "Task created"))
        task_id = out[2].split()
        return task_id[1] if len(task_id) else ""

    def list_tasks(self):
        return self._task_list()

    def stop_task(self, task_id):
        cmd = '{} task stop {}'.format(os.path.join(self.dir, self.name), task_id)
        log.debug("snaptel task stop")
        out = self._start_process(cmd).split('\n')
        return "Task stopped" in out[0]

    def task_hits_count(self, task_id):
        tasks = self._task_list()
        hits = 0
        for task in tasks:
            if task.split()[0] == task_id:
                hits += int(task.split()[3])

        log.debug("task hits {}".format(hits))
        return hits

    def task_fails_count(self, task_id):
        tasks = self._task_list()
        fails = 0
        for task in tasks:
            if task.split()[0] == task_id:
                fails += int(task.split()[5])

        log.debug("task fails {}".format(fails))
        return fails

    def list_metrics(self):
        cmd = '{} metric list'.format(os.path.join(self.dir, self.name))
        log.debug("snaptel metric list")
        metrics = self._start_process(cmd).split('\n')[1:-1]
        return filter(lambda e: e,  metrics)
    
    def metric_get(self, metric):
        cmd = '{} metric get -m {}'.format(os.path.join(self.dir, self.name), metric)
        log.debug("snaptel metric get -m {}".format(metric))
        out = self._start_process(cmd).split('\n')
        if len(out) < 8:
            return []
        out = out[5:]
        headers = map(lambda e: e.replace(" ", ""), filter(lambda e: e != "", out[0].split('\t')))
        rules = []
        for o in out[1:]:
            r = map(lambda e: e.replace(" ", ""), filter(lambda e: e != "", o.split('\t')))
            if len(r) == len(headers):
                rule = {}
                for i in range(len(headers)):
                    rule[headers[i]] = r[i]
                rules.append(rule)
        return rules

    def _task_list(self):
        cmd = '{} task list'.format(os.path.join(self.dir, self.name))
        tasks = self._start_process(cmd).split('\n')[1:]
        tasks = filter(lambda t: t != '', tasks)
        return tasks if len(tasks) else []

    def _start_process(self, cmd):
        process = subprocess.Popen(cmd.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err:
            self.errors.append(err)
        return out


class Binaries(object):

    def __init__(self):
        self._snapteld = None
        self._snaptel = None
        self._collector = None
        self._publisher = None
        self._processor = None

    @property
    def snapteld(self):
        return self._snapteld

    @snapteld.setter
    def snapteld(self, s):
        self._snapteld = s

    @property
    def snaptel(self):
        return self._snaptel

    @snaptel.setter
    def snaptel(self, s):
        self._snaptel = s

    @property
    def collector(self):
        return self._collector

    @collector.setter
    def collector(self, c):
        self._collector = c

    @property
    def processor(self):
        return self._processor

    @processor.setter
    def processor(self, p):
        self._processor = p

    @property
    def publisher(self):
        return self._publisher

    @publisher.setter
    def publisher(self, p):
        self._publisher = p

    def get_all_bins(self):
        all_bins = [self.snapteld, self.snaptel, self.collector, self.processor, self.publisher]
        return filter(lambda b: b, all_bins)

    def get_all_plugins(self):
        all_plugins = [self.collector, self.processor, self.publisher]
        return filter(lambda p: p, all_plugins)

    def __str__(self):
        return ";".join(map(lambda e: e.name, self.get_all_bins()))
