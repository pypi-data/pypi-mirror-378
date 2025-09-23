from typing import Union
from attr import define, field
from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf, open_dict
from hydra import initialize, compose

def resolve_hydra_config(cfg: DictConfig) -> DictConfig:
    return OmegaConf.structured(OmegaConf.to_yaml(cfg, resolve=True))


def load_hydra_config(version_base='1.3', config_path=f"../../configs", config_name="server.yaml") -> open_dict:
    with initialize(version_base=version_base, config_path=config_path):
        hydra_cfg = compose(config_name=config_name)
    return hydra_cfg

@define
class BaseSettings:
    hydra_config_name = field(default="config.yaml", type=str)
    hydra_config_path = field(default="../../../configs", type=str)
    hydra_version_base = field(default="1.3", type=str)
    hydra_config = field(default=None, type=Union[DictConfig, None])

    def __attrs_post_init__(self):
        self.hydra_config = load_hydra_config(version_base=self.hydra_version_base, config_path=self.hydra_config_path,
                                              config_name=self.hydra_config_name)

    def convert_to_dict(self,data) -> dict:
        factory = instantiate(data, _partial_=True, _convert_="all")
        return factory
setting = BaseSettings()
print(setting.hydra_config)