#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com

# multithreading
import concurrent.futures
import json
import jsonschema
import os
import os.path
import shutil
# from multiprocessing import Pool
import subprocess
from pathlib import Path

import s3lib
import ziplib

# this variable determines the default behavior, to exit when an error is found. Individual tasks override this behavior
EXIT_ON_ERROR = True


# get the input data for all the sites we are going to process
def get_input_files(mode: str, tmp_zip_dir: str, fetches: list):
    return_code = 0

    # TODO: move elsewhere or change default
    remove_zips = True

    for fetch in fetches:
        exit_on_error = EXIT_ON_ERROR
        if 'exitOnError' in fetch:
            exit_on_error = fetch['exitOnError']

        name: str = fetch['name']

        if 'includeWhenMode' in fetch:
            include_when_mode = fetch['includeWhenMode']
            if mode not in include_when_mode:
                print(f'skipping fetch task {name} in mode {mode}')
                continue
        if 'excludeWhenMode' in fetch:
            exclude_when_mode = fetch['excludeWhenMode']
            if mode in exclude_when_mode:
                print(f'skipping fetch task {name} in mode {mode}')
                continue

        bucket: str = fetch['bucket']
        key: str = fetch['key']
        dest: str = fetch['dest']
        expand: bool = fetch['expand']

        # fetch file from S3
        return_code = s3lib.copy_s3_object(bucket, key, dest)
        if exit_on_error and return_code != 0:
            break
            # unzip the inputs, prepare input files
        elif expand:
            ret = ziplib.expand(dest, Path(dest).parent)
            if exit_on_error and return_code != 0:
                break
            elif remove_zips:
                os.remove(dest)

        if 'excludeFilePattern' in fetch:
            patterns = fetch['excludeFilePattern']
            files = [f for f in Path(dest.replace('.7z', '')).iterdir() if any(f.match(p) for p in patterns)]
            for file in files:
                print(f'removing file: {file}')
                os.remove(file)

        return return_code


def run_tasks(process_list: list, mode: str):
    logFolder = "./logs"

    # create logs folder if it doesn't exist
    os.makedirs(logFolder, exist_ok=True)

    for process in process_list:
        exit_on_error = EXIT_ON_ERROR
        if 'exitOnError' in process:
            exit_on_error = process['exitOnError']

        # apply run mode logic - skip processes as needed
        proc_name = process["name"]

        if 'includeWhenMode' in process:
            include_when_mode = process['includeWhenMode']
            if mode not in include_when_mode:
                print(f'skipping process task {proc_name} in mode {mode}')
                continue
        if 'excludeWhenMode' in process:
            exclude_when_mode = process['excludeWhenMode']
            if mode in exclude_when_mode:
                print(f'skipping process task {proc_name} in mode {mode}')
                continue

        # create the output directory when provided
        output_folder = None
        if 'outputFolder' in process:
            output_folder = process["outputFolder"]
            os.makedirs(output_folder, exist_ok=True)

        # generate index of input files, when file pattern is specified
        file_pattern = None
        if 'inputFilePattern' in process:
            file_pattern = process["inputFilePattern"]

        if (file_pattern == None):
            # create an empty work list so that we execute the command that was provided
            work_list = ['']
        else:
            inputFolder = process["inputFolder"]
            work_list = []
            # get files - recursive matches
            files = Path(inputFolder).rglob(file_pattern)
            for file in files:
                work_list.append(file)

            if len(work_list) == 0:
                print(f"Error preparing {proc_name} work list. No files found in {file_pattern}")
                return_code = 232
                if exit_on_error:
                    break

        log_behavior = None
        if 'logBehavior' in process:
            log_behavior = process['logBehavior']

        # run the current process
        return_code = manage_process(proc_name, work_list, process["command"], log_behavior, exit_on_error)
        if exit_on_error and return_code != 0:
            print("Errors found processing " + proc_name + ", ending early")
            break

    return return_code


# delegate for running external executables
def process_runner(process_name: str, item: int, items: int, cmd: str):
    escapedCmd = cmd.replace("\n", "\\n")
    print(f'starting: [{process_name}] #{item}/{items} [{escapedCmd}]')
    return subprocess.run(cmd, shell=True)
    # print(f'stopping: #{item}')


# ************************************************************************************************************
# manageProcess 
# manages the execution of programs across the available CPUs
# ************************************************************************************************************
def manage_process(process_name: str, work_list: list, command: str, log_behavior: str, exit_on_error: bool):
    return_code = 0
    log_folder = "./logs"
    counter = 0

    # read in the index file, which list the files to run
    process_count = len(work_list)

    # count the processors once, and run with all
    processor_count = len(os.sched_getaffinity(0))
    print(f"processes to run: {process_count}, processors available: {processor_count}")

    # if there are fewer processes to run than processors, use only processCount threads
    if process_count < processor_count:
        processor_count = process_count

    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=processor_count) as executor:
        for inputFilePath in work_list:
            counter += 1

            command = command.replace('[INPUT_FILE_PATH]', str(inputFilePath))
            cmd = command

            if log_behavior is None:
                log_file_str = str(inputFilePath).replace('/', '-').replace('.in', '').replace('.txt', '')
                log_file_out = os.path.join(log_folder, process_name + "-" + log_file_str + ".log")
                log_file_err = os.path.join(log_folder, process_name + "-" + log_file_str + ".err")
                cmd += f' >{log_file_out} 2>{log_file_err}'

            futures.append(executor.submit(process_runner, process_name, counter, len(work_list), cmd))

        for future in concurrent.futures.as_completed(futures):
            process_result = future.result()
            # print(processResult)
            if exit_on_error and process_result.returncode != 0:
                return_code = process_result.returncode
                break

    if return_code != 0:
        # post-process the error log files. Remove them if empty, report them if not
        print(f"error running {process_name}...")
        files = Path(log_folder).glob(f"{process_name}-*.err")

        for file in files:
            if Path(file).stat().st_size == 0:
                os.remove(file)
            else:
                with open(file) as myfile:
                    a_errs = myfile.readlines()
                sErrs = '\n'.join(map(str, a_errs))
                subject = f"errors found processing {process_name}, file: {file}"
                message = "contents: " + sErrs

                print(subject + ". " + message)
    return return_code


def move_files(move_tasks: list, mode: str):
    for task in move_tasks:
        exit_on_error = EXIT_ON_ERROR
        if 'exitOnError' in task:
            exit_on_error = task['exitOnError']

        name = task['name']
        if 'includeWhenMode' in task:
            include_when_mode = task['includeWhenMode']
            if mode not in include_when_mode:
                print(f'skipping move task {name} in mode {mode}')
                continue
        if 'excludeWhenMode' in task:
            exclude_when_mode = task['excludeWhenMode']
            if mode in exclude_when_mode:
                print(f'skipping move task {name} in mode {mode}')
                continue

        input_folder = task['inputFolder']
        include_file_pattern = task['includeFilePattern']
        output_folder = task['outputFolder']

        exclude_file_pattern = None
        if 'excludeFilePattern' in task:
            exclude_file_pattern = task['excludeFilePattern']

        if Path(input_folder).exists():
            for includePattern in include_file_pattern:
                for file in Path(input_folder).rglob(includePattern):
                    if exclude_file_pattern is None or not (True in [file.match(p) for p in exclude_file_pattern]):

                        try:
                            os.makedirs(output_folder, exist_ok=True)
                            print(f'moving {file} to {output_folder}')

                            # if another file already exists in the location, remove it
                            if Path(output_folder).joinpath(file.name).exists():
                                os.remove(Path(output_folder).joinpath(file.name))

                            shutil.move(str(file), output_folder)
                        except Exception as err:
                            err_str = f"failed to move {str(file)} to {output_folder}, error: {str(err)}"
                            if exit_on_error:
                                print(f"error: {err_str}")
                                return 213
                            else:
                                print(f"warning: {err_str}")


def prepare_outputs(tasks_store: list, mode: str):
    return_code = 0

    for task in tasks_store:
        exit_on_error = EXIT_ON_ERROR
        if 'exitOnError' in task:
            exit_on_error = task['exitOnError']

        name = task['name']

        if 'includeWhenMode' in task:
            include_when_mode = task['includeWhenMode']
            if mode not in include_when_mode:
                print(f'skipping storage task {name} in mode {mode}')
                continue
        if 'excludeWhenMode' in task:
            exclude_when_mode = task['excludeWhenMode']
            if mode in exclude_when_mode:
                print(f'skipping storage task {name} in mode {mode}')
                continue

        bucket = task['bucket']
        dest = task['dest']
        source = task['source']
        compress: bool = task['compress']

        remove_on_store = False
        if 'removeOnStore' in task:
            remove_on_store = task['removeOnStore']

        if Path(source).exists():
            if len(list(Path(source).glob('*'))) == 0:
                print(f"skipping empty output directory for storage task [{name}]: {source}")
            else:
                print(f"saving outputs: {source}")

                if compress:
                    src_dir = str(Path(source))
                    # trim trailing / character
                    if src_dir[-1] == '/':
                        src_dir = src_dir[0:-1]
                    tmpZip = src_dir + ".7z"

                    return_code = ziplib.compress(destination_path=src_dir, source_path=tmpZip)
                    if exit_on_error and return_code != 0:
                        break

                    return_code = s3lib.write_s3_object(bucket, dest, tmpZip)
                    if exit_on_error and return_code != 0:
                        break

                    if remove_on_store:
                        os.remove(tmpZip)
                else:
                    return_code = s3lib.put_files(bucket, source, dest)
                    if exit_on_error and return_code != 0:
                        break

    return return_code


def get_validated_task_config(json_data_path: str):
    cfg = None
    script_dir = Path(__file__).parent
    json_schema_path = script_dir.joinpath('tasks.schema.json')

    if json_data_path is None or json_data_path == '':
        # default TASKS FILE
        json_data_path = script_dir.joinpath('tasks.json')
    else:
        json_data_path = Path(json_data_path)

    if json_data_path.exists() and json_schema_path.exists():
        with open(json_data_path, 'r') as file:
            # do environment variable parameter substitution here
            tasks_json = os.path.expandvars(file.read())
            cfg = json.loads(tasks_json)

        with open(json_schema_path, 'r') as file:
            tasks_schema = file.read()
            schema = json.loads(tasks_schema)

        try:
            jsonschema.validate(instance=cfg, schema=schema)
        except jsonschema.exceptions.ValidationError as err:
            print(f'error, cannot validate json schema: {err}')
            return None
    return cfg
