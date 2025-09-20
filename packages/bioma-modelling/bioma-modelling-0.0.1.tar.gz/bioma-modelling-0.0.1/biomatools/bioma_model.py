import inspect
import json
import logging

from biomatools.utils.abs import (
    AbstractBioMAComponent,
    AbstractBioMAClient,
    AbstractBioMAObject,
)
from biomatools.utils.formats import (
    check_bioma_type,
    is_bioma_table,
    json_serialize_component,
)
from biomatools.utils.naming import BIOMA_SIMPLE_TYPES


class BioMAConfiguration(AbstractBioMAComponent):
    """A Configuration item inside the BioMA call"""

    def __init__(
        self,
        assembly_qualified_name,
        client: AbstractBioMAClient = None,
        recursive: bool = False,
    ):
        # assembly qualified name
        self.BioMAtype = assembly_qualified_name
        # configuration variables
        self.vars = {}
        self.subtypes = []
        self.configurations = {}
        if client:
            self.load_subtypes(client, recursive)
            self.load_configurations(client)

    def load_configurations(self, client: AbstractBioMAClient):
        """
        Retrieves all possible configuration items of the current BioMA component
        supported by the passed client
        """
        if any(basetype in self.BioMAtype for basetype in BIOMA_SIMPLE_TYPES):
            self.configurations = {}
        else:
            self.configurations = client.get_object_configuration(self.BioMAtype)

    def load_subtypes(self, client: AbstractBioMAClient, recursive: bool = False):
        """
        Retrieves all possible subtypes of the current BioMA component
        supported by the passed client
        """
        if any(basetype in self.BioMAtype for basetype in BIOMA_SIMPLE_TYPES):
            self.subtypes = []
        elif recursive:
            self.subtypes = [
                BioMAConfiguration(i, client)
                for i in client.get_object_subtypes(self.BioMAtype)
            ]
        else:
            self.subtypes = [
                BioMAConfiguration(i)
                for i in client.get_object_subtypes(self.BioMAtype)
            ]

    def set_param(
        self, parname: str, parvalue=None, client: AbstractBioMAClient = None
    ):
        self.vars[parname] = parvalue
        if parname in self.configurations:
            # we now that parameter! Let's check its type
            if isinstance(parvalue, AbstractBioMAComponent) and (client is not None):
                if not check_bioma_type(
                    self.configurations.get(parname), parvalue, client
                ):
                    logging.warning(
                        f"Incompatible BioMA type at {parname}: expected {self.configurations.get(parname).BioMAtype}, found {parvalue.BioMAtype}"
                    )
        else:
            logging.warning(
                f"Parameter {parname} not found in {self.BioMAtype} configuration"
            )

    def describe(self):
        '''It returns a human understandable view of the component'''
        shorthand = self.BioMAtype.split(',')[0]
        out= f'Component {shorthand}\n\nFully qualified name: {self.BioMAtype}'
        if len(self.vars) > 0:
            out = out + '\n\nConfigured Variables\n'
            for k, v in self.vars.items():
                out = out + f'+ {k} : {v}\n'
            out = out + '\n'
        if len(self.configurations)>0:
            out = out + '\n\nAllowed Configurations\n'
            for k, v in self.configurations.items():
                out = out + f'+ {k} : {v}\n'
            out = out + '\n'
        if len(self.subtypes)>0:
            out = out + '\n\nSubtypes\n'
            for  v in self.subtypes:
                out = out + f'+ {v}\n'
            out = out + '\n'
        return out

    def toJSON(self):
        return json.dumps(
            {"@type": self.BioMAtype} | self.vars,
            default=json_serialize_component,
            sort_keys=True,
            indent=4,
        )

    def toDict(self):
        return {"@type": self.BioMAtype} | {self.vars}

    def json_serialize(self):
        serialized_vars = {}
        for k, v in self.vars.items():
            if isinstance(v, AbstractBioMAObject):
                # serialization is recursive!
                serialized_vars[k] = v.json_serialize()
            else:
                serialized_vars[k] = v

        return {"@type": self.BioMAtype} | serialized_vars

    @classmethod
    def from_dict(cls, env: dict, client:AbstractBioMAClient=None):
        """This is mostly used to build the object from the output returned by Web Services"""
        if isinstance(env, dict):
            if "@type" in env:
                out = cls(env["@type"], client=client)
                for parname, parvalue in env.items():
                    if parname != "@type":
                        if isinstance(parvalue, dict):
                            # is it another BioMA component?
                            if (
                                "@type" in parvalue
                            ):  # @type has already been taken care of
                                out.set_param(
                                    parname=parname,
                                    parvalue=BioMAConfiguration.from_dict(parvalue),
                                )
                            else:
                                out.set_param(parname=parname, parvalue=parvalue)
                        else:
                            # here it's anything but a dictionary
                            out.set_param(parname=parname, parvalue=parvalue)
                    # if parname is @type we don't do anything
                return out
            else:
                raise ValueError(f"No @type attribute in the provided dictionary")

        else:
            raise ValueError(f"Expected a dictionary, got {type(env)}")
        
    
    def __str__(self):
        return f'{type(self)} of type {self.BioMAtype.split(",")[0]}'
    def __repr__(self):
        return self.__str__()
