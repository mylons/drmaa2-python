import unittest
import drmaa2
import os

import mock

from hamcrest import assert_that, starts_with, ends_with, is_, has_properties, equal_to, contains, has_item

QSUB_OUTPUT = "Your job 764188 (\"lyonstest\") has been submitted"


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
        if os.path.isfile(self.script_path):
            os.remove(self.script_path)

    @mock.patch('drmaa2.backend.shell.qsub')
    def test_run_job_with_contact(self, mock_qsub):
        mock_qsub.return_value = QSUB_OUTPUT
        session = drmaa2.create_job_session("session_name", "contact")
        jt = drmaa2.JobTemplate(remote_command='/bin/sleep', script_path=self.script_path)
        job = session.run_job(jt)
        # TODO test wait terminated somehow
        #job.wait_terminated(drmaa2.INFINITE_TIME)

        assert_that(job, has_properties({'remote_command': equal_to('/bin/sleep'),
                                         'script_path': equal_to(self.script_path)}))

        with open(self.script_path, 'r') as f:
            lines = f.readlines()
            assert_that(lines[0], starts_with('#!/usr/bin/env'))
            assert_that(lines[0], ends_with('bash\n'))

    @mock.patch('drmaa2.backend.shell.qsub')
    def test_job_script_is_written_correctly(self, mock_qsub):
        mock_qsub.return_value = QSUB_OUTPUT
        session = drmaa2.create_job_session("session_name", "contact")
        jt = drmaa2.JobTemplate(remote_command='/bin/sleep', script_path=self.script_path,
                                queue_name='dev-short', use_cwd=True)
        job = session.run_job(jt)

        assert_that(job, has_properties({'remote_command': equal_to('/bin/sleep'),
                                         'queue_name': equal_to('dev-short'),
                                         'use_cwd': equal_to(True),
                                         'script_path': equal_to(self.script_path)}))

        with open(self.script_path, 'r') as f:
            lines = f.readlines()
            assert_that(lines, has_item('#!/usr/bin/env bash\n'))
            assert_that(lines, has_item('#$ -cwd\n'))
            assert_that(lines, has_item('/bin/sleep\n'))
            assert_that(lines, has_item('#$ -q dev-short\n'))

if __name__ == '__main__':
    unittest.main()
