#!/usr/bin python
from brew.importing.brew_importer import BrewImporter
from recipes.beerparser import *
import utils.brewutils
import utils.logging as log


class BeerSmithImporter(BrewImporter):
    def __init__(self):
        BrewImporter.__init__(self)
        self.display_name = 'Beer Smith'
        self.recipe_file = ''
        self.counter = 0

    def do_import(self, uri):
        try:
            if uri is None:
                return 0
            self.recipe_file = uri
            log.debug('Loading recipe file {0}...'.format(self.recipe_file))
            beer = BeerParser()
            recipedata = beer.get_recipes(self.recipe_file)
            self.counter = 0
            for item in recipedata:
                name = utils.brewutils.lookup_brew_name(item).strip()
                if name is not None:
                    # Save to database
                    brew, sections = utils.brewutils.create_brew_model(item)
                    brew.save()
                    self.counter += 1
                    s_count = m_count = b_count = f_count = 0
                    for section in sections:
                        s_count += 1
                        s = utils.brewutils.create_section(section, brew, s_count)
                        s.save()
                        for step in section.steps:
                            brew_step = None
                            if s.worker_type == 'MashWorker':
                                m_count += 1
                                brew_step = utils.brewutils.create_mash_step(step, s, m_count)
                            elif s.worker_type == 'BoilWorker':
                                b_count += 1
                                brew_step = utils.brewutils.create_boil_step(step, s, b_count)
                            elif s.worker_type == 'FermentationWorker':
                                f_count += 1
                                brew_step = utils.brewutils.create_fermentation_step(step, s, f_count)
                            if brew_step is not None:
                                brew_step.save()
            log.debug('...done loading recipe file {0}'.format(self.recipe_file))
        except Exception, e:
            log.error('Failed to load recipes {0} ({1})'.format(self.recipe_file, e.message))
        return self.counter