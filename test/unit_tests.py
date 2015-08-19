import unittest
import drmaa2
import os

import mock

QSUB_OUTPUT = "Your job 764188 (\"lyonstest\") has been submitted"

def qsub(job):
    return QSUB_OUTPUT

class GeneralTestCase(unittest.TestCase):
    def test_struct_empty_init(self):
        """ Make sure that the data structures are properly initialized. """
        queue_info = drmaa2.QueueInfo()
        self.assertEqual(queue_info.name, None)

    def test_struct_param_init(self):
        """ Test data structure initialization on creation. """
        jt = drmaa2.JobTemplate(**{'remote_command': '/bin/sleep', 'submit_as_hold': True})
        self.assertEqual(jt.remote_command, '/bin/sleep')
        self.assertEqual(jt.submit_as_hold, True)

    def test_struct_backend_specific_attrs(self):
        """ Test that implementation-specific attributes are supported. """
        jt = drmaa2.JobTemplate()
        # TODO test more of the members here, the ones i care about especially
        self.assertEqual(jt.parallel_environment, None)


class SessionManagerTestCase(unittest.TestCase):
    def test_describe_attribute(self):
        drmaa2.describe_attribute(drmaa2.Notification(), "session_name")

    def test_supports(self):
        self.assertEqual(drmaa2.supports(drmaa2.Capability.CALLBACK), True)
        self.assertEqual(drmaa2.supports(drmaa2.Capability.ADVANCE_RESERVATION), True)

    def test_job_session(self):
        session = drmaa2.create_job_session()
        name = session.session_name
        session.close()
        session = drmaa2.open_job_session(name)
        session.close()
        drmaa2.destroy_session(name)

    def test_reservation_session(self):
        session = drmaa2.create_reservation_session()
        name = session.session_name
        session.close()
        session = drmaa2.open_reservation_session(name)
        session.close()
        drmaa2.destroy_session(name)

    def test_monitoring_session(self):
        session = drmaa2.open_monitoring_session()
        session.close()

    def test_get_job_session_names(self):
        drmaa2.get_job_session_names()

    def test_get_reservation_session_names(self):
        drmaa2.get_reservation_session_names()

    def _callback(notification):
        pass

    def test_register_event_notification(self):
        drmaa2.register_event_notification(self._callback)


class MonitoringSessionTestCase(unittest.TestCase):
    def test_get_all_jobs(self):
        session = drmaa2.open_monitoring_session("Foo")
        session.get_all_jobs("foo")


class JobSessionTestCase(unittest.TestCase):

    def setUp(self):
        self.script_path = "/tmp/drmaa2.sge"

    def tearDown(self):
        os.remove(self.script_path)

    @mock.patch('drmaa2.util.ge.qsub', side_effect=qsub)
    def test_run_job_with_contact(self, mock_os):
        session = drmaa2.create_job_session("session_name", "contact")
        jt = drmaa2.JobTemplate(remote_command='/bin/sleep', script_path=self.script_path)
        job = session.run_job(jt)
        job.wait_terminated(drmaa2.INFINITE_TIME)

    @mock.patch('drmaa2.util.ge.qsub', side_effect=qsub)
    def test_run_job_without_contact(self, mock_os):
        session = drmaa2.create_job_session()
        jt = drmaa2.JobTemplate(remote_command='/bin/sleep', script_path=self.script_path)
        job = session.run_job(jt)
        job.wait_terminated(drmaa2.INFINITE_TIME)


if __name__ == '__main__':
    unittest.main()
