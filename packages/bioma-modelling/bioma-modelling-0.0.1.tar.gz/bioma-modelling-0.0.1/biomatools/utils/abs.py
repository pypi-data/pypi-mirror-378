from abc import ABC, abstractmethod
import json


class AbstractBioMAClient(ABC):
    @abstractmethod
    def get_initial_configuration(self):
        pass

    @abstractmethod
    def get_object_configuration(self, assembly_qualified_name: str):
        pass

    @abstractmethod
    def get_object_subtypes(self, assembly_qualified_name: str):
        pass

    @abstractmethod
    def list_models(self):
        pass

    @abstractmethod
    def run(self, idx):
        pass

    @abstractmethod
    def run_all(self):
        pass


class AbstractBioMAObject(ABC):

    def toJSON(self) -> str:
        """Serializes item into a JSON STRING"""
        return json.dumps(self.json_serialize())

    def to_dict(self) -> dict:
        """Serializes item into a Dictionary"""
        return vars(self)

    @abstractmethod
    def json_serialize(self):
        """turns the item into something that is JSON serializable"""
        pass


class AbstractBioMATable(AbstractBioMAObject):

    @abstractmethod
    def to_df(self):
        pass


class AbstractBioMAComponent(AbstractBioMAObject):
    @abstractmethod
    def load_configurations(self, client: AbstractBioMAClient):
        pass

    @abstractmethod
    def load_subtypes(self, client: AbstractBioMAClient, recursive: bool = False):
        pass

    @abstractmethod
    def set_param(self, parname: str, parvalue=None):
        pass

    @abstractmethod
    def describe(self):
        pass
