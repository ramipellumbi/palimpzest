#!/usr/bin/env python3
import palimpzest as pz

import argparse
import yaml
import os
import sys

if __name__ == "__main__":
    env_dir = os.getenv("PZ_DIR")

    parser = argparse.ArgumentParser(prog='pz', description='Palimpzest management tool')

    # specify config directory manually (overrides environment variable)
    parser.add_argument("--dir", type=str, default=env_dir, help="Path to the PZ working dir")

    # Individual commands
    parser.add_argument("--init", action="store_true", help="Initialize a data directory")
    parser.add_argument("--lsdata", action="store_true", help="Verbose output")

    # Subparser for the 'registerdatafile' command
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')
    parser_register = subparsers.add_parser('registerdatafile', help='Register a file in the data repository')
    parser_register.add_argument('filename', type=str, help='File to register')
    parser_register.add_argument('name', type=str, help='Name to register the file under')

    # Subparser for 'registerdatadir' command
    parser_register = subparsers.add_parser('registerdatadir', help='Register a dir in the data repository')
    parser_register.add_argument('filedir', type=str, help='Directory to register')
    parser_register.add_argument('name', type=str, help='Name to register the file under')

    # Subparser for the 'rmdata' command
    parser_rmdata = subparsers.add_parser('rmdata', help='Remove a data object in the data repository')
    parser_rmdata.add_argument('name', type=str, help='Name to remove from the data repository')

    # Parse the arguments
    args = parser.parse_args()
    if args.dir is None:
        raise Exception("No configuration information available. Set PZ_DIR or use --dir")

    # Get the working directory info
    workingdir = None
    if args.init:
        config = pz.Config(os.path.abspath(args.dir), create=True)
        sys.exit(0)
    
    config = pz.Config(os.path.abspath(args.dir))

    # Process the usert command
    if args.command == 'registerdatafile':        
        pz.DataDirectory().registerLocalFile(os.path.abspath(args.filename), args.name)
    elif args.command == 'registerdatadir':
        pz.DataDirectory().registerLocalDirectory(os.path.abspath(args.filedir), args.name)
    elif args.lsdata:
        ds = pz.DataDirectory().listRegisteredDatasets()

        from prettytable import PrettyTable
        table = [["Name", "Type", "Path"]]
        for path, descriptor in ds:
            table.append([path, descriptor[0], descriptor[1]])

        t = PrettyTable(table[0])
        t.add_rows(table[1:])
        print(t)
        print()
        print("Total datasets:", len(table)-1)
    elif args.command == 'rmdata':
        pz.DataDirectory().rmRegisteredDataset(args.name)
        print("Deleted", args.name)
    else:
        parser.print_help()
