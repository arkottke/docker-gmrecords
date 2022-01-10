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
def process_fetches(mode: str, tmp_zip_dir: str, fetches: list, prior_errors:bool = False):
    return_code = 0

    # TODO: move elsewhere or change default
    remove_zips = True

    for fetch in fetches:
        required = False
        if 'required' in fetch:
            required = fetch['required']
        # skip a store task when there are prior errors UNLESS task is required
        if not required and prior_errors:
            continue

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

        expand = False
        if 'expand' in fetch:
            expand = fetch['expand']

        if expand:
            # allows the user to specify a directory for dest path
            if key.endswith('.7z') and not dest.endswith('.7z'):
                dest = os.path.join(dest, os.path.basename(key))

        # fetch file from S3
        rc = s3lib.get_files(bucket, key, dest, filter=None)
        # return_code = s3lib.copy_s3_object(bucket, key, dest)
        if exit_on_error and rc != 0:
            return_code = rc
            break
        elif expand:
            # unzip the inputs, prepare input files
            expand_to = Path(dest).parent
            
            return_code = ziplib.expand(dest, expand_to)
            if exit_on_error and return_code != 0:
                break
            elif remove_zips:
                if len(dest) > 3 and dest[-3:] == '.7z':
                    os.remove(dest)
                elif dest.endswith('/'):
                    for file in Path(dest).glob('*.7z'):
                        file.unlink()

        if 'excludeFilePattern' in fetch:
            patterns = fetch['excludeFilePattern']
            files = [f for f in Path(dest.replace('.7z', '')).iterdir() if any(f.match(p) for p in patterns)]
            for file in files:
                print(f'removing file: {file}')
                os.remove(file)

    return return_code


def run_tasks(process_list: list, mode: str, prior_errors:bool = False):
    logFolder = "./logs"
    return_code = 0
    
    # create logs folder if it doesn't exist
    os.makedirs(logFolder, exist_ok=True)

    for process in process_list:
        required = False
        if 'required' in process:
            required = process['required']
        # skip a store task when there are prior errors UNLESS task is required
        if not required and prior_errors:
            continue

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
                if exit_on_error:
                    return_code = 232
                    break

        log_behavior = None
        if 'logBehavior' in process:
            log_behavior = process['logBehavior']

        # run the current process
        rc = manage_process(proc_name, work_list, process["command"], log_behavior, exit_on_error)
        if exit_on_error and rc != 0:
            print("errors found processing " + proc_name + ", ending early")
            return_code = rc
            break

    return return_code


# delegate for running external executables
def process_runner(process_name: str, item: int, items: int, cmd: str):
    escapedCmd = cmd.replace("\n", "\\n")
    print(f'starting: [{process_name}] #{item}/{items} [{escapedCmd}]')
    return subprocess.run(cmd, shell=True)


# ************************************************************************************************************
# manageProcess 
# manages the execution of programs across the available CPUs
# ************************************************************************************************************
def manage_process(process_name: str, work_list: list, command: str, log_behavior: str, exit_on_error: bool):
    return_code = 0
    log_folder = "logs"
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

            cmd = command.replace('[INPUT_FILE_PATH]', str(inputFilePath))

            if log_behavior == 'capture':
                log_file_str = str(inputFilePath).replace('/', '-').replace('.in', '').replace('.txt', '')
                log_file_out = os.path.join(log_folder, process_name + "-" + log_file_str + ".log")
                log_file_err = os.path.join(log_folder, process_name + "-" + log_file_str + ".err")
                cmd += f' >{log_file_out} 2>{log_file_err}'

            futures.append(executor.submit(process_runner, process_name, counter, len(work_list), cmd))

        for future in concurrent.futures.as_completed(futures):
            try:
                process_result = future.result()
                if exit_on_error and process_result.returncode != 0:
                    return_code = process_result.returncode
            except Exception as err:
                print(f'error in process: {str(err)}')
                if exit_on_error:
                    return_code = 244

    # remove any empty err files
    files = Path(log_folder).glob(f"{process_name}-*.err")
    for file in files:
        if Path(file).stat().st_size == 0:
            os.remove(file)

    if return_code != 0:
        # post-process the error log files. report any non-empty error files
        print(f"error running {process_name}...")
        files = Path(log_folder).glob(f"{process_name}-*.err")
        logs = ''
        for file in files:
            with open(file) as myfile:
                a_errs = myfile.readlines()
            errs = '\n'.join(map(str, a_errs))

            log_file = str(file).replace('.err','.log')
            if Path(log_file).stat().st_size > 0:
                with open(log_file) as myfile2:
                    a_logs = myfile2.readlines()
                if len(a_logs) > 10:
                    # only display the last 10 lines
                    a_logs = a_logs[len(a_logs)-10:len(a_logs)-1]
                logs = '\n'.join(map(str, a_logs))

            subject = f"errors found processing {process_name}, file: {file}"
            message = f"contents: {logs}\nErrors:\n{errs}"

            print(subject + ". " + message)
    return return_code


def move_files(move_tasks: list, mode: str, prior_errors:bool = False):
    return_code = 0
    
    for task in move_tasks:
        required = False
        if 'required' in task:
            required = task['required']
        # skip a store task when there are prior errors UNLESS task is required
        if not required and prior_errors:
            continue

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
    return return_code


def process_store(tasks_store: list, mode: str, prior_errors:bool = False):
    return_code = 0

    for task in tasks_store:
        required = False
        if 'required' in task:
            required = task['required']
        # skip a store task when there are prior errors UNLESS task is required
        if not required and prior_errors:
            continue

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

        compress = False
        if 'compress' in task:
            compress = task['compress']

        compressSubDirectories = False
        if 'compressSubDirectories' in task:
            compressSubDirectories = task['compressSubDirectories']

        remove_on_store = True
        if 'removeOnStore' in task:
            remove_on_store = task['removeOnStore']

        if not Path(source).exists():
            print(f'error: source path for store task [{name}] does not exists: {source}')
            if exit_on_error:
                return_code = 43
                break
        else:
            contents = []
            is_empty = False
            if Path(source).is_dir():
                contents = list(Path(source).glob('*'))
                if not compressSubDirectories:
                    # is there anything to zip?
                    is_empty = (len(contents) == 0)
                else:
                    # when compressing subdirectories, pre-check that at least one exists
                    for item in contents:
                        if item.is_dir() and len(list(item.glob('*'))) > 0:
                            is_empty = False
                            break

            if is_empty:
                print(f"skipping empty output directory for storage task [{name}]: {source}")
            else:
                print(f"saving outputs: {source}")

                if compressSubDirectories and len(contents) > 0:
                    for dir in contents:
                        if dir.is_dir():
                            src = str(dir)

                            # trim trailing / character
                            if src[-1] == '/':
                                src = src[0:-1]
                            tmp_zip = src + ".7z"

                            rc = ziplib.compress(source_path=src, zip_path=tmp_zip)
                            if exit_on_error and rc != 0:
                                return_code = rc
                                break

                            key = Path(dest).joinpath(Path(tmp_zip).name)

                            rc = s3lib.write_s3_object(bucket_name=bucket, key=str(key), file=tmp_zip)
                            if exit_on_error and rc != 0:
                                return_code = rc
                                break

                            if remove_on_store:
                                os.remove(tmp_zip)
                elif compress:
                    src = str(Path(source))
                    # trim trailing / character
                    if src[-1] == '/':
                        src = src[0:-1]
                    tmp_zip = src + ".7z"

                    rc = ziplib.compress(source_path=src, zip_path=tmp_zip)
                    if exit_on_error and rc != 0:
                        return_code = rc
                        break

                    if dest[-1] == '/':
                        key = Path(dest).joinpath(Path(tmp_zip).name)
                    else:
                        key = dest

                    rc = s3lib.write_s3_object(bucket_name=bucket, key=str(key), file=tmp_zip)
                    if exit_on_error and rc != 0:
                        return_code = rc
                        break

                    if remove_on_store:
                        os.remove(tmp_zip)
                else:
                    if Path(source).is_dir():
                        rc = s3lib.put_files(bucket_name=bucket, local_folder=source, prefix=dest)
                    else:
                        # handle case where a directory name is specified for the destination
                        if dest[-1] == '/':
                            key = Path(dest).joinpath(Path(source).name)
                        else:
                            key = dest

                        rc = s3lib.write_s3_object(bucket_name=bucket, key=str(key), file=source)
                    if exit_on_error and rc != 0:
                        return_code = rc
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

    if json_data_path.exists():
        with open(json_data_path, 'r') as file:
            # do environment variable parameter substitution here
            tasks_json = os.path.expandvars(file.read())
            cfg = json.loads(tasks_json)

        if not json_schema_path.exists():
            print(f'warning, skipping validation of json against schema, cannot find schema file: {json_schema_path}')
        else:
            with open(json_schema_path, 'r') as file:
                tasks_schema = file.read()
                schema = json.loads(tasks_schema)
            try:
                jsonschema.validate(instance=cfg, schema=schema)
            except jsonschema.exceptions.ValidationError as err:
                print(f'error, cannot validate json schema: {err}')
                return None
    return cfg
