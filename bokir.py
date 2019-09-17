import os
import re
import sys
import argparse
import subprocess
import configparser
from sys import argv

def read_config():
    
    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    _ns = config['bokir']['namespace']
    _env = config['bokir']['env']

    return [_ns,_env];

def check_param(_ns,_env):
    
    cfg_ini = read_config()
    if not _ns:
        _ns = cfg_ini[0]
    else:
        _ns = _ns    
    if not _env:
        _env = cfg_ini[1]
    else:
        _env = _env
    
    return [_ns,_env]

def set_context():

    # read config file
    cfg_ini = read_config()
    # get values of environment
    _env = cfg_ini[1]
    # get context based on environment
    cmd =  "kubectl config get-contexts | grep "+_env+" | awk \'{ print $2 }\'"
    process = subprocess.run(cmd,stdout=subprocess.PIPE, shell=True)
    
    # output of subprocess will be byte, we need to decode that into string
    output = str(process.stdout, encoding='utf-8')

    # set context
    cmd = "kubectl config set-context {}".format(output)
    process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = str(process.stdout, encoding='utf-8')
    print(output)

def update_config(args):

    config = configparser.ConfigParser()
    config.read('config.ini')
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
    _filepath = os.path.realpath("{}.yaml").format(_cm)
    cmd = "kubectl apply -f "+_filepath
    process = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    output = str(process.stdout, encoding='utf-8')
    print(output)    

def menus():
    # create top-level parser
    parser = argparse.ArgumentParser(prog='bokir',
        description='Configmap extractor tools',
        epilog='si Bolot yang jadi mandor nye!!',
        add_help=True)

    # create subparser    
    subparsers = parser.add_subparsers()

    # create parser for 'list configmap' command
    listconfig = subparsers.add_parser('get', description='List all configmap per namespaces', add_help=True)
    listconfig.add_argument('-ns', action='store', dest='_ns', type=str, help='Namespaces of application')
    listconfig.add_argument('-env', action='store', dest='_env', type=str, help='Environment [ prod | stg | dev ]')
    listconfig.add_argument('-all', action='store_true', dest='_all', help='All configmap')
    listconfig.set_defaults(func=get_cm)

    # create parser for 'exporting configmap' command
    exportconfig = subparsers.add_parser('export', description='Export configmap into a file', add_help=True)
    exportconfig.add_argument('-ns',  action='store', dest='_ns', type=str, help='Namespaces of application')
    exportconfig.add_argument('-cm', action='store', dest='_cm', type=str, required=True, help='ConfigMap names')
    exportconfig.add_argument('-env', action='store', dest='_env',type=str, default=None, help='Environment [ prod | stg | dev ]')
    exportconfig.set_defaults(func=export_cm)

    # create parser for 'applying configmap' command
    updateconfig = subparsers.add_parser('update', description='Update configmap from a file', add_help=True)
    updateconfig.add_argument('-cm', action='store', dest='_cm', type=str, required=True, help='ConfigMap names')
    updateconfig.set_defaults(func=upload_cm)
    
    # create parser for 'update config.ini' command
    updateconfig = subparsers.add_parser('config', description='Update config.ini section', add_help=True)
    updateconfig.add_argument('-ns', action='store', dest='_ns', type=str, help='Update namespace')
    updateconfig.add_argument('-env', action='store', dest='_env', type=str, help='Update environment')
    updateconfig.set_defaults(func=update_config)

    parser.add_argument('--version', action='version', version='%(prog)s 0.9')
    
    try:
        results = parser.parse_args()
        # invoke func
        results.func(results)
    except:

        # if user didn't pass any arguments
        # print help
        parser.print_help()
        
        # kill pid
        sys.exit(0)


def main():
    menus()

if __name__ == "__main__":
    main()
