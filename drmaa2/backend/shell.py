""" DRMAA2 Python language binding.

    This is a implementation from the command line utilities: qstat, qacct, etc

    For further information, please visit drmaa.org.
"""
from operator import attrgetter

import drmaa2

import collections

# Definition part
from drmaa2.util import render_template, namedtuple_from_dict, spec_to_reality
from drmaa2.util.ge import qacct, parse_qacct, qsub, parse_qsub_output, qmod, qrls, qdel
# taken directly from output of qacct

common_job_keys = ['qname']

univa_command_line_output_keys = ['hostname', 'group', 'owner', 'project', 'department', 'jobname',
                                  'jobnumber', 'taskid', 'account', 'failed', 'cpu', 'mem', 'io', 'iow', 'maxvmem',
                                  'arid', 'jc_name',
                                  ] + common_job_keys
job_template_impl_spec = [
    # the below are added by me because there's nothing that makes sense for this
    'parallel_environment', 'export_environment_variables', 'is_binary_file', 'use_cwd',
    'job_depends_on', 'job_is_array', 'array_task_first', 'array_task_last', 'array_task_step_size',
    'script_path'
] + common_job_keys
job_info_impl_spec = univa_command_line_output_keys + [
    'qsub_time', 'start_time', 'end_time', 'granted_pe',
    'ru_wallclock', 'ru_utime', 'ru_stime', 'ru_maxrss',
    'ru_ixrss', 'ru_ismrss', 'ru_idrss', 'ru_isrss', 'ru_minflt', 'ru_majflt', 'ru_nswap',
    'ru_inblock', 'ru_oublock', 'ru_msgsnd', 'ru_msgrcv', 'ru_nsignals', 'ru_nvcsw', 'ru_nivcsw',
]
reservation_template_impl_spec = []
reservation_info_impl_spec = []
queue_info_impl_spec = []
machine_info_impl_spec = []
notification_impl_spec = []

CORE_FILE_SIZE = "CORE_FILE_SIZE"
CPU_TIME = "CPU_TIME"
DATA_SIZE = "DATA_SIZE"
FILE_SIZE = "FILE_SIZE"
OPEN_FILES = "OPEN_FILES"
STACK_SIZE = "STACK_SIZE"
VIRTUAL_MEMORY = "VIRTUAL_MEMORY"
WALLCLOCK_TIME = "WALLCLOCK_TIME"

drms_name = "Shell DRM"
drms_version = {'major': 1, 'minor': 0}
drmaa_name = "Shell DRM DRMAA Implementation"
drmaa_version = {'major': 2, 'minor': 0}

# Implementation part

app_callback = None


def describe_attribute(instance, name):
    return name


class MonitoringSession(drmaa2.MonitoringSession):
    def get_all_reservations(self):
        return []

    def get_all_jobs(self, the_filter):
        return []

    def get_all_queues(self, names):
        return []

    def get_all_machines(self, names):
        return []

    def close(self):
        pass


class JobArray(drmaa2.JobArray, collections.Iterable):
    """
    # TODO implement some validation for this constration:
    'array_task_step_size',
                 1 <= array_task_first  <= MIN(2^31-1, max_aj_tasks)
                 1 <= array_task_last <= MIN(2^31-1, max_aj_tasks)
                 array_task_first <= array_task_last
    """

    def reap(self):
        super(JobArray, self).reap()

    def release(self):
        super(JobArray, self).release()

    def hold(self):
        super(JobArray, self).hold()

    def resume(self):
        super(JobArray, self).resume()

    def terminate(self):
        super(JobArray, self).terminate()

    def suspend(self):
        super(JobArray, self).suspend()

    def __init__(self, jobs=[]):
        # sort by taskid
        self.jobs = sorted(jobs, key=attrgetter('taskid'))

    def __iter__(self):
        return iter(self.jobs)


class JobSession(drmaa2.JobSession):

    contact = None  # in Univa it's apparently always none
    session_name = None
    job_categories = None

    def __init__(self):
        self.session_jobs = []

    def get_jobs(self, the_filter=None):
        """
        :param the_filter: a function that takes a job and returns true or false
        :return:
        """
        if the_filter:
            return [job for job in self.session_jobs if the_filter(job)]
        else:
            return self.session_jobs

    def get_job_array(self, job_array_id):
        return JobArray(parse_qacct(qacct(job_id=job_array_id)))

    def run_job(self, job_template):
        """
        what does it take to run a job?
        1: build a job object from template
        2:  if job_template.working_directory
                write script to that directory
            else
                write script to cwd and use -cwd by setting job_template.use_cwd
        3: qsub the job
        :param job_template: JobTemplate
        :return: Job
        """
        job = Job.from_template(job_template)
        with open(job.script_path, 'w') as script:
            script.write(render_template(**spec_to_reality(**job.job_template._asdict())))

        qsub_output = qsub(job)
        job_id, job_name = parse_qsub_output(qsub_output)
        job.job_id = job_id
        job.job_name = job_name

        self.session_jobs.append(job)

        return job

    def run_bulk_jobs(self, job_template, begin_index, end_index, step, max_parallel):
        return JobArray()

    def wait_any_started(self, jobs, timeout):
        return Job()

    def wait_any_terminated(self, jobs, timeout):
        return Job()

    def close(self):
        """
        for the command line parsing version I don't think this has to do anything at all
        :return:
        """
        pass


class ReservationSession:
    contact = None
    session_name = None

    def get_reservation(self, reservation_id):
        #return Reservation()
        raise NotImplementedError("not sure if I will implement this one")

    def request_reservation(self, reservation_template):
        #return Reservation()
        raise NotImplementedError("not sure if I will implement this one")

    def get_reservations(self):
        #return []
        raise NotImplementedError("not sure if I will implement this one")

    def close(self):
        #pass
        raise NotImplementedError("not sure if I will implement this one")


class Job(drmaa2.Job):

    session_name = None
    absolute_script_path = None

    def _init_from_dict(self, d):
        fields_of_interest = set(drmaa2.JobTemplate._fields + drmaa2.JobInfo._fields)
        for key, value in d.iteritems():
            if key in fields_of_interest and value:
                setattr(self, key, value)

    @classmethod
    def from_template(cls, job_template):
        job = cls()
        job.job_info = namedtuple_from_dict(job_template.__dict__, drmaa2.JobInfo)
        job.job_template = job_template
        job._init_from_dict(spec_to_reality(**job_template.__dict__))
        return job

    @classmethod
    def from_info(cls, job_info):
        job = cls()
        job.job_info = job_info
        job._init_from_dict(spec_to_reality(**job_info.__dict__))
        return job

    def suspend(self):
        qmod(self, suspend=True)

    def resume(self):
        qrls(self, resume=True)

    def hold(self):
        qrls(self, hold=True)

    def release(self):
        self.resume(self)

    def terminate(self):
        qdel(self)

    def reap(self):
        # TODO gotta think about this one
        pass

    def get_state(self):
        # TODO where does state come from?
        return JobState.RUNNING, "Running like hell."

    def get_info(self):
        # output of qacct
        return self.job_info

    def wait_started(self, timeout):
        pass

    def wait_terminated(self, timeout):
        pass

    @property
    def job_id(self):
        return self._job_id

    @job_id.setter
    def job_id(self, value):
        # maybe do some type checking here
        self._job_id = value

    @job_id.deleter
    def job_id(self):
        del self._job_id

    @property
    def job_template(self):
        return self._job_template

    @job_template.setter
    def job_template(self, job_template):
        self._job_template = job_template

    @job_template.deleter
    def job_template(self):
        del self._job_template


# Module-level functions


def describe_attribute(instance, name):
    return name


def supports(capability):
    if capability in (drmaa2.Capability.CALLBACK, drmaa2.Capability.ADVANCE_RESERVATION):
        return True
    else:
        return False


def create_job_session(session_name=None, contact=None):
    return JobSession()


def create_reservation_session(session_name=None, contact=None):
    return ReservationSession()


def open_job_session(session_name):
    return JobSession()


def open_reservation_session(session_name):
    return ReservationSession()


def open_monitoring_session(contact=None):
    return MonitoringSession()


def destroy_session(session):
    pass


def get_job_session_names():
    return []


def get_reservation_session_names():
    return []


def register_event_notification(callback):
    app_callback = callback
