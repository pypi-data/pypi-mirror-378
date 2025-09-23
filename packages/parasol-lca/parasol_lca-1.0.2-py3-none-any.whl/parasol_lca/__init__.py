# coding=utf-8
from . import _parameters
from . import _activities

class ParasolLCA:
    def __init__(self, target_database, version):
        """
        Create new ParasolLCA

        Parameters
        ----------
        target_database : str
            Name of the database to use to store parasol activities
        version : str
            Version string of ecoinvent database such as "3.7", "3.9" ...

        Returns
        -------
        ParasolLCA

        """
        self.prefix = "[parasol] "
        self.version = version
        self.target_database = target_database
        self.biosphere = f"ecoinvent-{version}-biosphere"
        self.technosphere = f"ecoinvent-{version}-cutoff"

    @staticmethod
    def from_dict(d : dict):
        """
        Create ParasolLCA from dictionnary

        Parameters
        ----------
        d : dict
        expected keys:
            - target_database = database to use to store new activities (string)
            - version = ecoinvent version used (string)
            - (optional) prefix = prefix for created activities (string)
            - (optional) biosphere = biosphere database name (string)
            - (optional) technosphere = technosphere database name (string)

        Returns
        -------
        ParasolLCA

        """
        conf = ParasolLCA(d["target_database"], d["version"])
        conf.prefix = d.get("prefix", conf.prefix)
        conf.biosphere = d.get("biosphere", conf.biosphere)
        conf.technosphere = d.get("technosphere", conf.technosphere)
        return conf

    def __getattr__(self, name):
        handler_name = f"_ensure_{name}"
        if not hasattr(_parameters, handler_name):
            raise AttributeError(f"Attribute {name} not found in ParasolLCA!")
        setattr(self, name, getattr(_parameters, handler_name)(self))
        # Should work
        return getattr(self, name)


def create(conf : ParasolLCA|dict):
    """Create the updated PV system dataset, related activities, and 2 impact
    models with PARASOL_LCA.

    Parameters
    ----------
    conf: dict
        expected keys:
            - target_database = database to use to store new activities (string)
            - version = ecoinvent version used (string)
            - (optional) prefix = prefix for created activities (string)
            - (optional) biosphere = biosphere database name (string)
            - (optional) technosphere = technosphere database name (string)

    """
    if isinstance(conf, dict):
        conf = ParasolLCA.from_dict(conf)
    #ensure_metalisation(conf)
    _activities._ensure_impact_model_per_kWh(conf)
    return conf
