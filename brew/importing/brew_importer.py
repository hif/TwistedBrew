#!/usr/bin python
import importlib
from brew import brew_import
import brew.brew_import

class ImporterRegistration():
    def __init__(self, index, display_name):
        self.index = index
        self.display_name = display_name


class BrewImporter():
    registered_importers = []
    importers_registered = False

    def __init__(self):
        self.display_name = 'do not register me'

    @staticmethod
    def get_importers():
        if not BrewImporter.importers_registered:
            BrewImporter.register()
        BrewImporter.importers_registered = True
        importers = []
        index = 0
        for importer in BrewImporter.registered_importers:
            importers.append(ImporterRegistration(index, importer.display_name))
        return importers

    @staticmethod
    def register():
        for importer_class in brew_import.BREW_IMPORTERS:
            class_data = importer_class.split(".")
            module_path = ".".join(class_data[:-1])
            class_name = class_data[-1]
            module = importlib.import_module(module_path)
            class_handle = getattr(module, class_name)
            importer = class_handle()
            BrewImporter.registered_importers.append(importer)

    @staticmethod
    def import_brews(index, uri):
        try:
            importer = BrewImporter.registered_importers[index]
            return importer.do_import(uri)
        except Exception:
            return 0

    # Implement this int the inheriting classes
    def do_import(self, index, uri):
        pass
