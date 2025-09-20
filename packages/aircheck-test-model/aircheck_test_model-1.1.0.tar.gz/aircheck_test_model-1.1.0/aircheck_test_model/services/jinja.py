from jinja2 import Environment, PackageLoader

env = Environment(
    loader=PackageLoader("aircheck_test_model"),
    autoescape=True,
)
