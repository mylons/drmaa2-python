
from jinja2 import Environment, PackageLoader


env = Environment(loader=PackageLoader('drmaa2', 'templates'))

job_template = env.get_template('sge_job.sh')


def namedtuple_from_dict(d, named_tuple_type):
    return named_tuple_type(**{k: v for k, v in d.iteritems() if k in named_tuple_type._fields})


def spec_to_reality(**kwargs):
    """
    this is used to reconcile the differences between the CLI and the object interface
    :param kwargs:
    :return:
    """
    cleaned_data = kwargs.copy()

    empirical = {'qname': 'queue_name',
                 'owner': 'job_owner',
                 'jobnumber': 'job_id'}

    spec = {'queue_name': 'qname',
            'job_name': 'jobname',
            'job_owner': 'owner',
            'job_id': 'jobnumber'}
    items = spec.items() + empirical.items()
    for k, v in items:
        if k in cleaned_data:
            cleaned_data[v] = cleaned_data[k]

    return cleaned_data

def render_template(**kwargs):
    """
    TODO: look deeper into ignored options to qsub:
            -adds, -ac, -binding, -c, -clear, -clearp -clears,
            -C, -dc, -dl, -hard, -jc, -js, -jsv, -m, -mods, -masterq,
            -mbind, -notify, -now, -M, -pty, -R, -r, -sc, -shell, -soft,
            -sync, -S, -tc, -terse, -verify, -w, -@
    TODO: something special for JobArray such that if it has dependencies it renders it specially
    :param kwargs:
    :return:
    """
    return job_template.render(**kwargs)
