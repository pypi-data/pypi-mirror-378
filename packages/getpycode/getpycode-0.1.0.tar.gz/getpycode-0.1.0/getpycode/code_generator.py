from jinja2 import Environment, BaseLoader, StrictUndefined

from getpycode.types import Package, Module


class CodeGenerator:
    def __init__(
        self,
        loader: BaseLoader,
        *,
        overwrite: bool = True
    ):
        self.environment = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
            undefined=StrictUndefined,
            loader=loader,
            auto_reload=False,
            extensions=["jinja2.ext.do"]
        )
        self._overwrite = overwrite

    def create_module(self, module: Module) -> None:
        if module.path.exists() and not self._overwrite:
            raise FileExistsError(f"Module {str(module.path)!r} already exists!")

        if module.template_path:
            template = self.environment.get_template(module.template_path)
            code = template.render(**module.fields)
        else:
            code = ""

        with module.path.open("w", encoding="utf-8") as file:
            file.write(code)

    def create_package(self, package: Package) -> None:
        package.path.mkdir(exist_ok=True)

        for i in package.modules:
            self.create_module(i)

        for i in package.packages:
            self.create_package(i)
