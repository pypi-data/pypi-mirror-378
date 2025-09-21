# -*- coding: utf-8 -*-

from soft_deps.api import MissingDependency

try:
    import bs4
except ImportError:  # pragma: no cover
    bs4 = MissingDependency("BeautifulSoup4", "pip install pythonic_gmail[email]")

try:
    import simple_aws_ssm_parameter_store.api as aws_ssm
except ImportError:
    aws_ssm = MissingDependency(
        "simple-aws-ssm-parameter-store", "pip install simple-aws-ssm-parameter-store"
    )
