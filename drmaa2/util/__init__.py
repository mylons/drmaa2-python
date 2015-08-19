
from jinja2 import Environment, PackageLoader


env = Environment(loader=PackageLoader('drmaa2', 'templates'))

job_template = env.get_template('sge_job.sh')



def clean_kwargs(**kwargs):
    cleaned_data = kwargs.copy()

    data_map = {'queue_name': 'qname', 'job_name': 'jobname'}

    for spec_name, empirical_name in data_map.iteritems():
        if spec_name in kwargs:
            cleaned_data[empirical_name] = kwargs[spec_name]

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
    return job_template.render(clean_kwargs(**kwargs))
