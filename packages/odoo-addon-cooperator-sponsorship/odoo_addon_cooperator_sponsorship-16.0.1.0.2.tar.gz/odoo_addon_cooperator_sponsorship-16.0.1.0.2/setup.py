import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        "depends_override": {"cooperator": "odoo-addon-cooperator==16.0.1.1.1.3"},
    },
)
