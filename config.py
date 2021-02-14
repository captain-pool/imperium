import re
import addict
import confuse


def singleton(instances):
  def singleton_fn(cls):
    def getinstance(*args, **kwargs):
      if kwargs.get("orphan"):
        kwargs.pop("orphan")
        return cls(*args, **kwargs)

      if cls not in instances:
        instances[cls] = cls(*args, **kwargs)
      return instances[cls]
    setattr(getinstance, "instances", cls.instances)
    return getinstance
  return singleton_fn


def snake_case(string):
  string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


class Config(addict.Dict):
  instances = {}

  def __init__(self, args=None):
    if args is None and not Config.instances:
      raise Exception("Initate a Config Instance First!")
    _parsed, config = self._parse(args, args.config)
    self._config = config
    second_copy = addict.Dict(_parsed)
    self.update(second_copy)

  @property
  def yaml(self):
    return self._config.dump()

  def dump(self, dumpath, content=None):
    with open(dumpath, "w") as f:
      f.write(content or self.yaml)

  def _parse(self, args, configs):
    config = confuse.Configuration("Config")
    for config_files in configs:
      config.set_file(config_files)
    config.set_args(args, dots=True)
    flattened = config.flatten()
    export_config_path = flattened.get("export_config_path")
    export_config = bool(flattened.get("export_config"))
    if export_config_path and export_config:
      Config.dump(export_config_path, config.dump())
    return flattened, config


Config = singleton(Config.instances)(Config)
