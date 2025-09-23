from dataclasses import dataclass


@dataclass
class Dataset:
    id: str

    @classmethod
    def upload_dataframe(cls,_transport,dataframe,name):
        return cls(_transport.upload_dataframe(dataframe,name))
