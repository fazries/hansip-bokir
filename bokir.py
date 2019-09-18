import argparse
import sys
import controller as ctrl

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
    listconfig.set_defaults(func=ctrl.get_cm)

    # create parser for 'exporting configmap' command
    exportconfig = subparsers.add_parser('export', description='Export configmap into a file', add_help=True)
    exportconfig.add_argument('-ns',  action='store', dest='_ns', type=str, help='Namespaces of application')
    exportconfig.add_argument('-cm', action='store', dest='_cm', type=str, required=True, help='ConfigMap names')
    exportconfig.add_argument('-env', action='store', dest='_env',type=str, default=None, help='Environment [ prod | stg | dev ]')
    exportconfig.set_defaults(func=ctrl.export_cm)

    # create parser for 'applying configmap' command
    updateconfig = subparsers.add_parser('update', description='Update configmap from a file', add_help=True)
    updateconfig.add_argument('-cm', action='store', dest='_cm', type=str, required=True, help='ConfigMap names')
    updateconfig.set_defaults(func=ctrl.upload_cm)
    
    # create parser for 'update config.ini' command
    updateconfig = subparsers.add_parser('config', description='Update config.ini section', add_help=True)
    updateconfig.add_argument('-ns', action='store', dest='_ns', type=str, help='Update namespace')
    updateconfig.add_argument('-env', action='store', dest='_env', type=str, help='Update environment')
    updateconfig.set_defaults(func=ctrl.update_config)

    parser.add_argument('--version', action='version', version='%(prog)s 0.9')
    
    try:
        results = parser.parse_args()
        # invoke func
        results.func(results)
    except:

        # if user didn't pass any arguments
        # print help
        #parser.print_help()
        
        # kill pid
        sys.exit(0)