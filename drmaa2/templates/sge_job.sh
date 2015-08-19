#!/usr/bin/env bash
#Begin GE Options
{%- if use_cwd %}
#$ -cwd
{% endif %}
{%- if parallel_environment %}
#$ -pe {{ parallel_environment }} {{ slots }}
{% endif %}
{%- if min_phys_memory %}
#$ -l mem={{ min_phys_memory }}
{% endif %}
{%- if qname %}
#$ -q {{ qname }}
{% endif %}
{%- if export_environment_variables -%}
#$ -V
{% endif %}
{%- if is_binary_file -%}
#$ -b y
{% endif %}
{%- if start_time %}
#$ -a {{ start_time }}
{% endif %}
{%- if accounting_id %}
#$ -A {{ accounting_id }}
{% endif %}
{%- if error_path %}
#$ -e {{ error_path }}
{% endif %}
{%- if submit_as_hold -%}
#$ -h
{% endif %}
{%- if job_depends_on and job_is_array %}
#$ -hold_jid_ad {{ job_depends_on }}
{% elif job_depends_on %}
#$ -hold_jid {{ job_depends_on }}
{% endif %}
{%- if input_path %}
#$ -i {{ input_path }}
{% endif %}
{%- if join_files %}
#$ -j y
{% endif %}
{%- if output_path %}
#$ -o {{ output_path }}
{% endif %}
{%- if job_is_array %}
#$ -t {{ array_task_first }}{% if array_task_last %}-{{array_task_last}}{% endif %}{% if array_task_step_size %}:{{ array_task_step_size }}{% endif %}
{% endif %}
{%- if job_environment %}
#$ -v {{ job_environment }}
{% endif %}
{%- if working_directory %}
#$ -wd {{ working_directory }}
{% endif %}
#End GE Options

#Begin User Computation

{{ remote_command }}

#End UserComputation
