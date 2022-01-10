#!/usr/bin/python3
# cloudburst framework - Bruce Hearn 2021 bruce.hearn@gmail.com
import boto3
import fwlib
import os
import os.path


def main():
    exit_code = -1

    # set from environment. These are set by in the container
    mode_str = os.getenv('MODE_STR')
    if mode_str is None or mode_str == '':
        mode_str = "default"

    aws_region = os.getenv('AWS_REGION')

    # optional parameters
    disk_stats = (os.getenv('DISK_STATS') == '1')
    local_mode = (os.getenv('LOCAL_MODE') == '1')

    # can override the default tasks.json with another path
    tasks_path = os.getenv('TASKS_PATH')

    log_folder = "./logs"
    os.makedirs(log_folder, exist_ok=True)

    cfg = fwlib.get_validated_task_config(tasks_path)
    if cfg is None:
        print(f"cannot continue as json tasks document is not valid")
    else:
        print(f"starting processing")
        if disk_stats:
            os.system('df -h')  # get linux disk space

        tmp_zip_dir = os.getcwd()
        if os.path.exists('/tmp/'):
            tmp_zip_dir = '/tmp'

        program = cfg['programName']
        item_name = cfg['itemName']
        print(
            f"processing: program [{program}] work item [{item_name}] mode [{mode_str}] local-mode [{local_mode}] region [{aws_region}]")
        boto3.setup_default_session(region_name=aws_region)

        exit_code = 0
        for element in cfg:
            try:
                if element == 'fetch':
                    fetches = cfg[element]
                    exit_code = fwlib.process_fetches(mode_str, tmp_zip_dir, fetches, exit_code != 0)

                    if disk_stats:
                        os.system("echo disk space: && df -h && echo disk usage: && du -ch")
                elif element == 'tasks':
                    tasks_processing = cfg[element]
                    exit_code = fwlib.run_tasks(tasks_processing, mode_str, exit_code != 0)

                elif element == 'move':
                    moves = cfg[element]
                    exit_code = fwlib.move_files(moves, mode_str, exit_code != 0)

                elif element == 'store':
                    if not local_mode:
                        tasks_store = cfg[element]
                        exit_code = fwlib.process_store(tasks_store, mode_str, exit_code != 0)
                    else:
                        exit_code = 0
                        print('skipping store tasks in local mode')
                else:
                    exit_code = 0

            except Exception as err:
                print(f"unexpected error: {str(err)}")
                exit_code = 4

        print("processing complete")

        # get linux disk space
        if disk_stats:
            os.system("echo Disk space: && df -h && echo disk usage: && du -ch")

    exit(exit_code)


if __name__ == "__main__":
    main()
