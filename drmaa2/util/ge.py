
import subprocess
import os
import re
from drmaa2 import Job


def parse_qacct(lines):
    jobs = []
    job_lines = []
    for line in lines:
        if line.startswith('='):
            # start of new job section -- reset array
            job_lines = []
            # advance, because this is the header and we do not care
            continue
        elif line.startswith('\n'):
            # we're at the end, create a new Job
            jobs.append(Job(job_lines))
        elif line.startswith("Total"):
            break
        else:
            job_lines.append(line)
    return jobs


def qacct(number_of_days=1, job_id=None):
    """
    runs qacct -d number_of_days -j
    :param number_of_days:
    :return: list of lines from the command
    """
    command_args = ['qacct', '-d', number_of_days, '-j']
    if job_id:
        command_args.append([job_id])
    return subprocess.check_output(command_args).split('\n')

def qsub(job):
    """
    changes to directory that the script is in, submits the job,
    returns the output of qsub, and changes back to the directory
    it came from.

    :param job: drmaa2.Job
    :return: qsub output
    """
    original_dir = os.getcwd()
    os.chdir(os.path.dirname(job.script_path))
    command_args = ['qsub', job.script_path]
    output = subprocess.check_output(command_args).split('\n')
    os.chdir(original_dir)
    return output


def parse_qsub_output(qsub_output):
    qsub_output_pat = re.compile('Your job (\d+) ("(\w+)")')
    m = qsub_output_pat.match(qsub_output)
    job_id, job_name = m.groups()
    return job_id, job_name
