#!/usr/bin/env python3

import argparse
import json
import shlex
import subprocess

filename = "/prolovote-data/votes.json"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n", "--name", type=str, help="name of the project", required=True
    )
    parser.add_argument(
        "-d",
        "--desc",
        type=str,
        help="description of the project",
        required=True,
    )
    args = parser.parse_args()

    new_project = dict()

    with open(filename, "r+") as fp:
        data = json.load(fp)
        fp.truncate(0)
        fp.seek(0)
        for elt in data["projects"]:
            if args.name == elt["project_name"]:
                print("This project is already there.")
                exit()
        new_project["index"] = len(data["projects"])
        new_project["project_name"] = args.name
        new_project["description"] = args.desc
        new_project["votes"] = 0
        data["projects"].append(new_project)
        json.dump(data, fp)

    subprocess.run(shlex.split("systemctl restart proloctf"), shell=False)
