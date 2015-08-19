[![Build Status](https://travis-ci.org/troeger/drmaa2-python.svg?branch=master)](https://travis-ci.org/troeger/drmaa2-python)

# DRMAA2 Python language binding

This repository offers an implementation for the DRMAA2 Python language.   

If you don't know what DRMAA is, please consult http://www.drmaa.org.

The code base is maintained @mylons. The intention to implement a version of the drmaa2 api without relying on C libs. This is pure python.

The `drmaa2/__init__.py` file is expected to remain untouched. If you see a need to change it, please talk to us, in order to maintain portability and standard compliance across all implementations.

## Compatibility

This code is designed to work with Python 2.6 and all later version, including Python 3. Implementers are encouraged to follow this convention.

## Note to DRMAA users

If you are looking for a DRMAA2 Python library for your cluster system, this is the RIGHT place!. Currently I'm only supporting Univa's implementation (which may work with others, but doubtful). It wouldn't be very difficult to extend this to other drmaa compliant systems

## Future plans

## Example

	import drmaa2
	session = drmaa2.create_job_session()
	jt = drmaa2.JobTemplate({'remoteCommand':'/bin/sleep'})
	job = session.run_job(jt)
	job.wait_terminated(drmaa2.INFINITE_TIME)

---
The OGF DRMAA Working Group <drmaa-wg@ogf.org>
