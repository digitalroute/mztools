#!/usr/bin/python3

from termcolor import colored
from subprocess import run, DEVNULL
from .common import get_parameter, list_s3_bucket_dirs
import os

def export_kubecfg(filename, state_bucket, cluster_name):
    kops_env=os.environ.copy()
    kops_env['KUBECONFIG']= filename
    try:
        kops = run(["kops", '--state=s3://'+state_bucket, "export", "kubecfg", cluster_name],
            stdout=DEVNULL,
            env=kops_env)
    except FileNotFoundError:
        print (colored('Could not execute `kops`, please install it according to https://github.com/kubernetes/kops', 'red', attrs=['bold']))
        return False
    return True

def find_kops_cluster_names(s3_bucketname, env):
    cluster_name=get_parameter('/'+env+'/kubernetes/cluster-name')
    cluster_candidates = list_s3_bucket_dirs(s3_bucketname)
    matching_clusters = list()
    for candidate in cluster_candidates:
        if cluster_name+'.'+env in candidate:
            matching_clusters.append(candidate)
    return matching_clusters

def find_single_cluster(kops_state_bucket, env):
    matching_clusters = find_kops_cluster_names(kops_state_bucket, env)
    if len(matching_clusters) > 1:
        print (colored('There are multiple matching cluster names in the state bucket - aborting',
            'red', attrs=['bold']))
        return None
    if len(matching_clusters) < 1:
        print (colored('There are no matching cluster names in the state bucket - aborting',
            'red', attrs=['bold']))
        return None
    return matching_clusters[0]

def get_state_bucket(env):
    return get_parameter('/'+env+'/kubernetes/state-bucket')
