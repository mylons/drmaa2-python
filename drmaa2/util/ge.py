
import subprocess
import os
import re
import drmaa2
from drmaa2.util import namedtuple_from_dict


def check_output_wrapper(command_args):
    return subprocess.check_output(command_args).split('\n')


def create_job_info(job_lines):
    d = {}
    for line in job_lines:
        if line.startswith('=') or line.startswith('\n'):
            # this is the header
            continue
        key, value = line.split(' ', 1)
        d[key] = value.strip()
    job_info = namedtuple_from_dict(d, drmaa2.JobInfo)
    return job_info


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
            jobs.append(drmaa2.Job(create_job_info(job_lines)))
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
    return check_output_wrapper(command_args)

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
    output = check_output_wrapper(command_args)
    os.chdir(original_dir)
    return output


def parse_qsub_output(qsub_output):
    qsub_output_pat = re.compile('Your job (\d+) \("(\w+)"\)')
    m = qsub_output_pat.match(qsub_output)
    job_id, job_name = m.groups()
    return job_id, job_name


def qmod(job, suspend=False):
    """
    :param job: drmaa2.Job -> the job should have already been submitted
    :return:
    """

    command_args = ['qmod']
    if suspend:
        command_args += ['-sj', job.job_id]

    output = check_output_wrapper(command_args)

    return output


def qrls(job):
    """

    :param job:
    :return:
    """
    command_args = ['qrls', job.job_id]
    return check_output_wrapper(command_args)


def qhold(job):
    """

    :param job:
    :return:
    """
    command_args = ['qrls', job.job_id]
    return check_output_wrapper(command_args)

def qdel(job):
    """

    :param job:
    :return:
    """

    command_args = ['qdel', job.job_id]
    return check_output_wrapper(command_args)
