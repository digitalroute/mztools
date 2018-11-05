#!/usr/bin/python3
from termcolor import colored

from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
from kubernetes.stream import stream
import os, sys, tempfile
from subprocess import run, DEVNULL, Popen, PIPE
from base64 import standard_b64decode

from .kops import export_kubecfg, get_state_bucket

class K8sexec:
    def __init__(self, config_file_name):
        self.load_config(config_file_name)

    def __init__(self, kops_state_bucket, kops_cluster_name):
        kubeconfig = tempfile.NamedTemporaryFile(delete=False)
        if not export_kubecfg(kubeconfig.name, kops_state_bucket, kops_cluster_name):
            sys.exit(1)
        self.load_config(kubeconfig.name)
        os.remove(kubeconfig.name)

    def load_config(self, config_file_name):
        config.load_kube_config(config_file=config_file_name)
        c = Configuration()
        c.assert_hostname = False
        Configuration.set_default(c)
        self.api = core_v1_api.CoreV1Api()

    def get_api(self):
        return self.api

    def find_pod_by_labels(self, labels):
        resp = None
        try:
            resp = self.api.list_namespaced_pod(namespace='default')
        except ApiException as e:
            if e.status != 404:
                print("Unknown error: %s" % e)
                exit(1)
        #{'items': [{'metadata': {'labels': {'app': 'platform',
        for pod in resp.items:
            for label, value in labels.items():
                if label not in pod.metadata.labels:
                    break
                if value != pod.metadata.labels[label]:
                    break
            else:
                return pod.metadata.name
        return None

    def exec_pod_command(self, command, labels = None, pod_name = None):
        result = { "stderr": [], "stdout": [], "success": False, "pod_name": None}
        if labels != None:
            pod_name = self.find_pod_by_labels(labels)
        if pod_name is None:
            return result
        result['pod_name'] = pod_name
        print(colored('Running command in in pod ' + pod_name, 'white'))
        exec_command = ['/bin/sh']
        resp = stream(self.api.connect_get_namespaced_pod_exec, pod_name, 'default',
                      command=exec_command,
                      stderr=True, stdin=True,
                      stdout=True, tty=False,
                      _preload_content=False)
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                result['stdout'].append(resp.read_stdout())
            if resp.peek_stderr():
                result['stderr'].append(resp.read_stderr())
            if command:
                c = command.pop(0)
                resp.write_stdin(c + "\n")
                result['success'] = True
            else:
                break

        resp.write_stdin("echo ALL done\n")

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                buf=resp.read_stdout(timeout=3)
                if buf is not None:
                    if 'ALL done' in buf:
                        result['stdout'].append(buf[:-9])
                        break
                    result['stdout'].append(buf)
            if resp.peek_stderr():
                result['stderr'].append(resp.read_stderr())
        resp.close()
        return result

    def delete_pod_directory(self, pod_name, dir):
        self.exec_pod_command(command=["rm -r " + dir], pod_name=pod_name)

    def tar_pod_directory(self, pod_name, dir):
        exec_command = ['/bin/sh']
        resp = stream(self.api.connect_get_namespaced_pod_exec, pod_name, 'default',
                      command=exec_command,
                      stderr=True, stdin=True,
                      stdout=True, tty=False,
                      _preload_content=False)

        resp.write_stdin("tar -C "+dir+" -cf - . | base64\n")
        resp.write_stdin("echo ALL done\n")

        result = { "stderr": [], "stdout": [], "success": False}
        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                buf=resp.read_stdout(timeout=3)
                if buf is not None:
                    if 'ALL done' in buf:
                        result['stdout'].append(buf[:-9])
                        break
                    result['stdout'].append(buf)
            if resp.peek_stderr():
                result['stderr'].append(resp.read_stderr())
        resp.close()
        return standard_b64decode("-".join(result['stdout']))
