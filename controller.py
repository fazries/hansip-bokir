import os
import re
import subprocess
import configparser


def read_config():
    
    config = configparser.ConfigParser()
    config.sections()
    config.read('conf/config.ini')
    _ns = config['bokir']['namespace']
    _env = config['bokir']['env']

    return [_ns,_env];

def check_param(_ns,_env):

     # read config file and iterate
    iter = read_config().__iter__()
    if not _ns:
        _ns = iter.__next__()
    else:
        _ns = _ns    
    if not _env:
        _env = iter.__next__()
    else:
        _env = _env
    
    return [_ns,_env]

def set_context():

    # read config file and iterate
    iter = read_config().__iter__()
    # get values of environment
    _ns  = iter.__next__()
    _env = iter.__next__()

    print(_env)
    # get context based on environment
    cmd =  "kubectl config get-contexts | grep "+_env+" | awk \'{ print $2 }\'"
    process = subprocess.run(cmd,stdout=subprocess.PIPE, shell=True)
    
    # output of subprocess will be byte, we need to decode that into string
    output = str(process.stdout, encoding='utf-8')

    # set context
    cmd = "kubectl config use-context {}".format(output)
    process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = str(process.stdout, encoding='utf-8')
    print(output)

def update_config(args):

    config = configparser.ConfigParser()
    config.read('conf/config.ini')
    a = config['bokir']
    
    print("current config")
    print("===============")
    for key in a:
        print(key +" = "+ a[key])
    print("\n")
    
    if not args._ns:
        _ns = a['namespace']
    else:
        _ns = args._ns    
    if not args._env:
        _env = a['env']
    else:
        _env = args._env
        stats = True

    a['namespace']  = _ns
    a['env']        = _env
    
    with open('config.ini','w') as configfile:
        config.write(configfile)
    print("new config")
    print("===========")
    for key in a:
        print(key +" = "+ a[key])

    print(stats)
    # set new context
    if stats == True:
        set_context()        

def get_cm(args):
    
    # set dictionary to call function check_param
    kwargs = {"_ns":args._ns,"_env":args._env}
    set_param = check_param(**kwargs)

    _all =  args._all

    # if true, get all cm based on labels in every namespaces
    if _all:
        cmd = "kubectl get cm -l app.kubernetes.io/instance='{}' --all-namespaces".format(set_param[1])
        process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        print(process.stdout)
    else:
        cmd = "kubectl -n {} get configmap".format(set_param[0])
        process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
        print(process.stdout)

def export_cm(args):

    # set dictionary to call function check_param
    kwargs = {"_ns":args._ns,"_env":args._env}
    set_param = check_param(**kwargs)

    _cm = args._cm
    
    cmd = "kubectl -n {} get configmap {} -o yaml".format(set_param[0],set_param[1])
    process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    
    # output of subprocess will be byte, we need to decode that into string
    output = str(process.stdout, encoding='utf-8')
    
    if process.returncode == 1:
        print("\nYour config map [ {} ] doesn't exist, kindly check your namespace name".format(_cm))
        print("added [ -ns ] to choose your namespace")
    else:    
        writefile = open("{}.yaml".format(_cm),"w")
        writefile.write(output)
        _filepath = os.path.realpath("{}.yaml").format(_cm)
        print("file configmap created\n"+_filepath)

def upload_cm(args):
    
    # remove all '.' from user input
    _cm = re.sub("\..+$","",args._cm)
    # get the path
    _filepath = os.path.realpath("{}.yaml").format(_cm)

    cmd = "kubectl apply -f "+_filepath
    
    process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = str(process.stdout, encoding='utf-8')
    print(output)