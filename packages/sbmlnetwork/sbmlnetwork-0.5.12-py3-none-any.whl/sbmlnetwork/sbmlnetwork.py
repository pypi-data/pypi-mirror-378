import libsbmlnetwork
import networkinfotranslator
import os
from IPython.display import display
from .settings import Settings
from .features.data_integration import ColorCodingFluxes
from .features.data_integration import ColorCodingConcentrations, SizeCodingConcentrations
from .network_elements import *
from .network_elements.visual_elements import *
from typing import Union
import warnings


class SBMLNetwork:

    def __init__(self):
        self.libsbmlnetwork = libsbmlnetwork.LibSBMLNetwork()
        self.settings = Settings(self.libsbmlnetwork)
        self.fluxes = None
        self.concentrations = None

    def load(self, sbml: str):
        if os.path.exists(sbml) or sbml.startswith("<?xml"):
            self.libsbmlnetwork.load(sbml)
        else:
            try:
                import tellurium as te
                self.libsbmlnetwork.load(te.loada(sbml).getSBML())
            except ImportError:
                raise ImportError("To load an Antimony model, please install full package using pip install \"sbmlnetwork[tellurium]\".")
        self.populate_settings()
        if self.libsbmlnetwork.getNumLayouts() == 0:
            self.auto_layout()
        elif self.libsbmlnetwork.getNumGlobalRenderInformation() == 0 and self.libsbmlnetwork.getNumLocalRenderInformation() == 0:
            self.auto_style()

        return self

    def save(self, file_name: str = None, update_network_extents: bool = False):
        if update_network_extents:
            self.update_network_extents()
        return self.libsbmlnetwork.save(file_name)

    def draw(self, file_name: str = None, update_network_extents: bool = False):
        """
        Draws the network of the SBML model. Saves the figure to the file_directory if specified, otherwise displays the figure.

        :param file_directory:
        :param file_name:
        :param update_network_extents: If True, updates the network extents before drawing the figure.
        """
        if update_network_extents:
            self.update_network_extents()
        if file_name:
            networkinfotranslator.import_sbml_export_figure(self.libsbmlnetwork, file_name,
                                                            self.settings.compartment_labels,
                                                            self.settings.species_labels,
                                                            self.settings.reaction_labels)
        else:
            display(networkinfotranslator.import_sbml_export_pil_image(self.libsbmlnetwork,
                                                                       self.settings.compartment_labels,
                                                                       self.settings.species_labels,
                                                                       self.settings.reaction_labels))

    def get_size(self):
        return self.libsbmlnetwork.getCanvasWidth(), self.libsbmlnetwork.getCanvasHeight()

    def set_size(self, size: tuple[int, int], adjust_elements: bool = True):
        previous_size = self.get_size()
        if self.libsbmlnetwork.setCanvasWidth(size[0]) == 0 and self.libsbmlnetwork.setCanvasHeight(size[1]) == 0:
            if adjust_elements:
                if size[0] < previous_size[0] or size[1] < previous_size[1]:
                    self.auto_layout()
                    warnings.warn("Some elements were repositioned to fit the new canvas size.")

                compartment_list = self.get_compartments_list()
                if len(compartment_list) == 1:
                    compartment_list[0].set_size(size)

                species_positions = self.get_species_list().get_positions()
                for species_position in species_positions:
                    if species_position[0] > size[0] or species_position[1] > size[1]:
                        warnings.warn("Some Species with set positions are outside the canvas size. Please adjust their positions or use a larger canvas size.")

            return True

        warnings.warn("The canvas size could not be set properly. Please use a larger canvas size.")
        return False

    @property
    def size(self):
        return self.get_size()

    @size.setter
    def size(self, size: tuple[int, int]):
        self.set_size(size)

    def get_compartment(self, compartment_id: str = None):
        if compartment_id is None and self.libsbmlnetwork.getNumAllCompartmentGlyphs() == 1:
            compartment_id = self.libsbmlnetwork.getListOfCompartmentIds()[0]
        if self.libsbmlnetwork.getNumCompartmentGlyphs(compartment_id=compartment_id) > 0:
            return Compartment(self.libsbmlnetwork, compartment_id, 0)

        return None

    def get_compartments_list(self, compartment_ids = None):
        compartments = CompartmentList(libsbmlnetwork=self.libsbmlnetwork)
        if compartment_ids is None:
            compartment_ids = self.libsbmlnetwork.getListOfCompartmentIds()
        elif isinstance(compartment_ids, str):
            compartment_ids = [compartment_ids]
        elif not isinstance(compartment_ids, list):
            raise ValueError("Compartment ids must be a string or a list of strings")
        for compartment_id in compartment_ids:
            for graphical_object_index in range(self.libsbmlnetwork.getNumCompartmentGlyphs(compartment_id=compartment_id)):
                compartments.append(Compartment(self.libsbmlnetwork, compartment_id, graphical_object_index))

        return compartments

    def get_compartment_ids(self):
        return self.libsbmlnetwork.getListOfCompartmentIds()

    @property
    def compartment(self):
        return self.get_compartment()

    @property
    def compartments(self):
        return self.get_compartments_list()

    @property
    def compartments_list(self):
        return self.get_compartments_list()

    @property
    def compartment_ids(self):
        return self.get_compartment_ids()



    def get_species(self, species_id: str):
        if self.libsbmlnetwork.getNumSpeciesGlyphs(species_id=species_id) > 0:
            return Species(self.libsbmlnetwork, species_id, 0)

        return None

    def get_species_list(self, species_ids = None):
        species = SpeciesList(libsbmlnetwork=self.libsbmlnetwork)
        if species_ids is None:
            species_ids = self.libsbmlnetwork.getListOfSpeciesIds()
        elif isinstance(species_ids, str):
            species_ids = [species_ids]
        elif not isinstance(species_ids, list):
            raise ValueError("Species ids must be a string or a list of strings")
        for species_id in species_ids:
            for graphical_object_index in range(self.libsbmlnetwork.getNumSpeciesGlyphs(species_id=species_id)):
                species.append(Species(self.libsbmlnetwork, species_id, graphical_object_index))

        return species

    def get_species_ids(self):
        return self.libsbmlnetwork.getListOfSpeciesIds()

    @property
    def species(self):
        return self.get_species_list()

    @property
    def species_list(self):
        return self.get_species_list()

    @property
    def species_ids(self):
        return self.get_species_ids()

    def get_reaction(self, reaction_id: str):
        if self.libsbmlnetwork.getNumReactionGlyphs(reaction_id=reaction_id) > 0:
            return Reaction(self.libsbmlnetwork, reaction_id, 0)

        return None

    def get_reactions_list(self, reaction_ids = None):
        reactions = ReactionList(libsbmlnetwork=self.libsbmlnetwork)
        if reaction_ids is None:
            reaction_ids = self.libsbmlnetwork.getListOfReactionIds()
        elif isinstance(reaction_ids, str):
            reaction_ids = [reaction_ids]
        elif not isinstance(reaction_ids, list):
            raise ValueError("Reaction ids must be a string or a list of strings")
        for reaction_id in reaction_ids:
            for graphical_object_index in range(self.libsbmlnetwork.getNumReactionGlyphs(reaction_id=reaction_id)):
                reactions.append(Reaction(self.libsbmlnetwork, reaction_id, graphical_object_index))

        return reactions

    def get_reaction_ids(self):
        return self.libsbmlnetwork.getListOfReactionIds()

    @property
    def reactions(self):
        return self.get_reactions_list()

    @property
    def reactions_list(self):
        return self.get_reactions_list()

    @property
    def reaction_ids(self):
        return self.get_reaction_ids()

    def get_independent_label(self, label: str):
        for i in range(self.libsbmlnetwork.getNumAllIndependentTextGlyphs()):
            if self.libsbmlnetwork.getIndependentTextGlyphId(i) == label or self.libsbmlnetwork.getText(self.libsbmlnetwork.getIndependentTextGlyphId(i)) == label:
                return Label(self.libsbmlnetwork, self.libsbmlnetwork.getIndependentTextGlyphId(i), 0, 0)

        return None

    def get_independent_labels(self):
        independent_lables = LabelList()
        for i in range(self.libsbmlnetwork.getNumAllIndependentTextGlyphs()):
            tg_id = self.libsbmlnetwork.getIndependentTextGlyphId(i)
            independent_lables.append(Label(self.libsbmlnetwork, tg_id, 0, 0))

        return independent_lables

    @property
    def independent_labels(self):
        return self.get_independent_labels()

    def add_independent_label(self, text, x, y, width, height):
        if self.libsbmlnetwork.addIndependentTextGlyph(text, x, y, width, height) == 0:
            tg_id = self.libsbmlnetwork.getIndependentTextGlyphId(self.libsbmlnetwork.getNumAllIndependentTextGlyphs() - 1)
            return Label(self.libsbmlnetwork, tg_id, 0, 0)

        return None

    def remove_independent_label(self, label):
        for i in range(self.libsbmlnetwork.getNumAllIndependentTextGlyphs()):
            if self.libsbmlnetwork.getIndependentTextGlyphId(i) == label or self.libsbmlnetwork.getText(self.libsbmlnetwork.getIndependentTextGlyphId(i)) == label:
                if self.libsbmlnetwork.removeIndependentTextGlyph(i) == 0:
                    return True
                else:
                    return False

        return False

    def get_additional_element(self, element_id: str):
        for i in range(self.libsbmlnetwork.getNumAllAdditionalGraphicalObjects()):
            if self.libsbmlnetwork.getAdditionalGraphicalObjectId(i) == element_id:
                return AdditionalElement(self.libsbmlnetwork, element_id)

        return None

    def get_additional_elements(self):
        additional_elements = NetworkElementList(libsbmlnetwork=self.libsbmlnetwork)
        for graphical_object_index in range(self.libsbmlnetwork.getNumAllAdditionalGraphicalObjects()):
            additional_elements.append(AdditionalElement(self.libsbmlnetwork, self.libsbmlnetwork.getAdditionalGraphicalObjectId(graphical_object_index)))

        return additional_elements

    @property
    def additional_elements(self):
        return self.get_additional_elements()

    def add_additional_element(self, element_id: str, element_type: str = "rectangle", position: tuple[float, float] = (0, 0), size: tuple[float, float] = (100, 100)):
        if element_id is None:
            raise ValueError("Element id cannot be None")
        valid_geometric_shapes = self.libsbmlnetwork.getListOfGeometricShapes()
        if element_type not in valid_geometric_shapes:
            raise ValueError(f"Element type must be one of {valid_geometric_shapes}")
        if self.libsbmlnetwork.addAdditionalGraphicalObject(id=element_id) == 0:
            if self.libsbmlnetwork.setGeometricShapeType(id=element_id, geometric_shape=element_type) == 0:
                if self.libsbmlnetwork.setX(id=element_id, x=position[0]) == 0 and \
                        self.libsbmlnetwork.setY(id=element_id, y=position[1]) == 0 and \
                        self.libsbmlnetwork.setWidth(id=element_id, width=size[0]) == 0 and \
                        self.libsbmlnetwork.setHeight(id=element_id, height=size[1]) == 0:
                    return AdditionalElement(self.libsbmlnetwork, element_id)
                else:
                    graphical_object_index = self.libsbmlnetwork.getNumAllAdditionalGraphicalObjects() - 1
                    self.libsbmlnetwork.removeAdditionalGraphicalObject(additional_graphical_object_index=graphical_object_index)

        return None

    def remove_additional_element(self, element: Union[str, AdditionalElement]):
        if isinstance(element, str):
            element = self.get_additional_element(element)
        if element is not None:
            element.remove_all_labels()
            for i in range(self.libsbmlnetwork.getNumAllAdditionalGraphicalObjects()):
                if self.libsbmlnetwork.getAdditionalGraphicalObjectId(i) == element.get_id():
                    if self.libsbmlnetwork.removeAdditionalGraphicalObject(additional_graphical_object_index=i) == 0:
                        return True

        return False

    # Todo: Implement get color options method

    def has_color_bar(self, color_bar_type: str = None):
        from .features.color_bar.color_bar_manager import ColorBarManager

        return ColorBarManager().has_color_bar(self, color_bar_type)

    def _add_color_bar(self, color_bar_type: str = None):
        from .features.color_bar.color_bar_manager import ColorBarManager

        return ColorBarManager().add_color_bar(self, color_bar_type)

    def get_color_bar(self, color_bar_type: str = None):
        from .features.color_bar.color_bar_manager import ColorBarManager

        return ColorBarManager().get_color_bar(self, color_bar_type)

    def remove_color_bar(self, color_bar_type: str = None):
        from .features.color_bar.color_bar_manager import ColorBarManager

        return ColorBarManager().remove_color_bar(self, color_bar_type)

    def remove_color_bars(self):
        from .features.color_bar.color_bar_manager import ColorBarManager

        return ColorBarManager().remove_color_bars(self)

    @property
    def color_bar(self):
        return self.get_color_bar()

    def get_background_color(self):
        return self.libsbmlnetwork.getBackgroundColor()

    def set_background_color(self, color: str):
        if self.libsbmlnetwork.setBackgroundColor(color) == 0:
            return True

        return False

    def set_font_color(self, color: str):
        self.get_compartments_list().set_font_colors(color)
        self.get_species_list().set_font_colors(color)
        self.get_reactions_list().set_font_colors(color)

    def get_font_color(self):
        all_font_colors = set()
        compartments_font_colors = self.get_compartments_list().get_font_colors()
        for font_color in compartments_font_colors:
            all_font_colors.add(font_color)
        species_font_colors = self.get_species_list().get_font_colors()
        for font_color in species_font_colors:
            all_font_colors.add(font_color)
        reactions_font_colors = self.get_reactions_list().get_font_colors()
        for font_color in reactions_font_colors:
            all_font_colors.add(font_color)

        if len(all_font_colors) > 1:
            return None

        return all_font_colors.pop()

    @property
    def font_color(self):
        return self.get_font_color()

    @font_color.setter
    def font_color(self, color: str):
        self.set_font_color(color)

    def set_font(self, font: str):
        self.get_compartments_list().set_fonts(font)
        self.get_species_list().set_fonts(font)
        self.get_reactions_list().set_fonts(font)

    def get_font(self):
        all_fonts = set()
        compartments_fonts = self.get_compartments_list().get_fonts()
        for font in compartments_fonts:
            all_fonts.add(font)
        species_fonts = self.get_species_list().get_fonts()
        for font in species_fonts:
            all_fonts.add(font)
        reactions_fonts = self.get_reactions_list().get_fonts()
        for font in reactions_fonts:
            all_fonts.add(font)

        if len(all_fonts) > 1:
            return None

        return all_fonts.pop()

    @property
    def font(self):
        return self.get_font()

    @font.setter
    def font(self, font: str):
        self.set_font(font)

    def set_font_size(self, size: float):
        self.get_compartments_list().set_font_sizes(size)
        self.get_species_list().set_font_sizes(size)
        self.get_reactions_list().set_font_sizes(size)

    def get_font_size(self):
        all_font_sizes = set()
        compartments_font_sizes = self.get_compartments_list().get_font_sizes()
        for font_size in compartments_font_sizes:
            all_font_sizes.add(font_size)
        species_font_sizes = self.get_species_list().get_font_sizes()
        for font_size in species_font_sizes:
            all_font_sizes.add(font_size)
        reactions_font_sizes = self.get_reactions_list().get_font_sizes()
        for font_size in reactions_font_sizes:
            all_font_sizes.add(font_size)

        if len(all_font_sizes) > 1:
            return None

        return all_font_sizes.pop()

    @property
    def font_size(self):
        return self.get_font_size()

    @font_size.setter
    def font_size(self, size: float):
        self.set_font_size(size)

    def set_text_bold(self, bold: bool):
        self.get_compartments_list().set_texts_bold(bold)
        self.get_species_list().set_texts_bold(bold)
        self.get_reactions_list().set_texts_bold(bold)

    def is_text_bold(self):
        all_text_bold = set()
        compartments_text_bold = self.get_compartments_list().are_texts_bold()
        for text_bold in compartments_text_bold:
            all_text_bold.add(text_bold)
        species_text_bold = self.get_species_list().are_texts_bold()
        for text_bold in species_text_bold:
            all_text_bold.add(text_bold)
        reactions_text_bold = self.get_reactions_list().are_texts_bold()
        for text_bold in reactions_text_bold:
            all_text_bold.add(text_bold)

        if len(all_text_bold) > 1:
            return None

        return all_text_bold.pop()

    @property
    def text_bold(self):
        return self.is_text_bold()

    @text_bold.setter
    def text_bold(self, bold: bool):
        self.set_text_bold(bold)

    def set_text_italic(self, italic: bool):
        self.get_compartments_list().set_texts_italic(italic)
        self.get_species_list().set_texts_italic(italic)
        self.get_reactions_list().set_texts_italic(italic)

    def is_text_italic(self):
        all_text_italic = set()
        compartments_text_italic = self.get_compartments_list().are_texts_italic()
        for text_italic in compartments_text_italic:
            all_text_italic.add(text_italic)
        species_text_italic = self.get_species_list().are_texts_italic()
        for text_italic in species_text_italic:
            all_text_italic.add(text_italic)
        reactions_text_italic = self.get_reactions_list().are_texts_italic()
        for text_italic in reactions_text_italic:
            all_text_italic.add(text_italic)

        if len(all_text_italic) > 1:
            return None

        return all_text_italic.pop()

    @property
    def text_italic(self):
        return self.is_text_italic()

    @text_italic.setter
    def text_italic(self, italic: bool):
        self.set_text_italic(italic)

    @property
    def background_color(self):
        return self.get_background_color()

    @background_color.setter
    def background_color(self, color: str):
        self.set_background_color(color)

    def set_border_color(self, color: str):
        self.get_compartments_list().set_border_colors(color)
        self.get_species_list().set_border_colors(color)
        self.get_reactions_list().set_border_colors(color)

    def get_border_color(self):
        all_border_colors = set()
        compartments_border_colors = self.get_compartments_list().get_border_colors()
        for border_color in compartments_border_colors:
            all_border_colors.add(border_color)
        species_border_colors = self.get_species_list().get_border_colors()
        for border_color in species_border_colors:
            all_border_colors.add(border_color)
        reactions_border_colors = self.get_reactions_list().get_border_colors()
        for border_color in reactions_border_colors:
            all_border_colors.add(border_color)

        if len(all_border_colors) > 1:
            return None

        return all_border_colors.pop()

    @property
    def border_color(self):
        return self.get_border_color()

    @border_color.setter
    def border_color(self, color: str):
        self.set_border_color(color)

    def set_border_thickness(self, thickness: float):
        self.get_compartments_list().set_border_thicknesses(thickness)
        self.get_species_list().set_border_thicknesses(thickness)
        self.get_reactions_list().set_border_thicknesses(thickness)

    def get_border_thickness(self):
        all_border_thicknesses = set()
        compartments_border_thicknesses = self.get_compartments_list().get_border_thicknesses()
        for border_thickness in compartments_border_thicknesses:
            all_border_thicknesses.add(border_thickness)
        species_border_thicknesses = self.get_species_list().get_border_thicknesses()
        for border_thickness in species_border_thicknesses:
            all_border_thicknesses.add(border_thickness)
        reactions_border_thicknesses = self.get_reactions_list().get_border_thicknesses()
        for border_thickness in reactions_border_thicknesses:
            all_border_thicknesses.add(border_thickness)

        if len(all_border_thicknesses) > 1:
            return None

        return all_border_thicknesses.pop()

    @property
    def border_thickness(self):
        return self.get_border_thickness()

    @border_thickness.setter
    def border_thickness(self, thickness: float):
        self.set_border_thickness(thickness)

    def set_fill_color(self, color: str):
        self.get_compartments_list().set_fill_colors(color)
        self.get_species_list().set_fill_colors(color)
        self.get_reactions_list().set_fill_colors(color)

    def get_fill_color(self):
        all_fill_colors = set()
        compartments_fill_colors = self.get_compartments_list().get_fill_colors()
        for fill_color in compartments_fill_colors:
            all_fill_colors.add(fill_color)
        species_fill_colors = self.get_species_list().get_fill_colors()
        for fill_color in species_fill_colors:
            all_fill_colors.add(fill_color)
        reactions_fill_colors = self.get_reactions_list().get_fill_colors()
        for fill_color in reactions_fill_colors:
            all_fill_colors.add(fill_color)

        if len(all_fill_colors) > 1:
            return None

        return all_fill_colors.pop()

    @property
    def fill_color(self):
        return self.get_fill_color()

    @fill_color.setter
    def fill_color(self, color: str):
        self.set_fill_color(color)

    def hide(self):
        self.get_compartments_list().hide()
        self.get_species_list().hide()
        self.get_reactions_list().hide()

    def show(self):
        self.get_compartments_list().show()
        self.get_species_list().show()
        self.get_reactions_list().show()

    # Todo: Implement get_colors_list method to return all valid colors
    # def get_colors_list(self):
    #     return self.libsbmlnetwork.getListOfColorIds()

    def get_style(self):
        return self.libsbmlnetwork.getStyle()

    def set_style(self, style_name: str):
        from .features.styles.style_manager import StyleManager

        style_manager = StyleManager(self)
        return style_manager.set_style(style_name)

    @property
    def style(self):
        return self.get_style()

    @style.setter
    def style(self, style_name: str):
        self.set_style(style_name)

    def get_styles_options(self):
        return self.libsbmlnetwork.getListOfStyles()

    def show_fluxes(self, data: Union[float, dict], log_scale: bool = False, min_threshold: float = None, skip_hidden_elements: bool = True):
        self.fluxes = ColorCodingFluxes(self, skip_hidden_elements)
        return self.fluxes.show(data, log_scale, min_threshold)

    def hide_fluxes(self):
        if self.fluxes is None:
            return False

        return self.fluxes.hide()

    def show_concentrations(self, data: Union[float, dict], log_scale: bool = False,
                            min_threshold: float = None, show_by = "color",
                            skip_hidden_elements: bool = True,
                            min_size: float = 10, max_size: float = 100):
        if show_by == "size":
            if min_size > max_size:
                raise ValueError("Minimum size must be less than maximum size")
            self.concentrations = SizeCodingConcentrations(self, min_size, max_size)
        else:
            self.concentrations = ColorCodingConcentrations(self, skip_hidden_elements)

        return self.concentrations.show(data, log_scale, min_threshold)

    def hide_concentrations(self):
        if self.concentrations is None:
            return False

        return self.concentrations.hide()

    def group_reactions(self, reactions: list[str, Reaction], color: str = None):
        from .features.grouping import ReactionGroup

        reaction_group = ReactionGroup()
        reaction_group.group(self, reactions, color)
        return reaction_group

    def create_aliases(self, alias_map):
        for reaction_id, species_ids in alias_map.items():
            reaction = self.get_reaction(reaction_id)
            for species_id in species_ids:
                self.get_species(species_id).create_alias(reaction)

    # ToDo: Implement the following functions on the list of elements
    # def show_compartment_labels(self):
    #     if self.libsbmlnetwork.enableDisplayCompartmentsTextLabel(True) == 0:
    #         return True
    #
    #     return False
    #
    # def hide_compartment_labels(self):
    #     if self.libsbmlnetwork.enableDisplayCompartmentsTextLabel(False) == 0:
    #         return True
    #
    #     return False
    #
    # def show_species_labels(self):
    #     if self.libsbmlnetwork.enableDisplaySpeciesTextLabel(True) == 0:
    #         return True
    #
    #     return False
    #
    # def hide_species_labels(self):
    #     if self.libsbmlnetwork.enableDisplaySpeciesTextLabel(False) == 0:
    #         return True
    #
    #     return False
    #
    # #ToDo: Check if it works properly
    # def show_reaction_labels(self):
    #     if self.libsbmlnetwork.enableDisplayReactionsTextLabel(True) == 0:
    #         return True
    #
    #     return False
    #
    # def hide_reaction_labels(self):
    #     if self.libsbmlnetwork.enableDisplayReactionsTextLabel(False) == 0:
    #         return True
    #
    #     return False
    #
    # def show_id_as_label(self):
    #     if self.libsbmlnetwork.setUseNameAsTextLabel(False) == 0:
    #         return True
    #
    #     return False
    #
    # def show_name_as_label(self):
    #     if self.libsbmlnetwork.setUseNameAsTextLabel(True) == 0:
    #         return True
    #
    #     return False

    def auto_layout(self, max_num_connected_edges: int = 3, reset_fixed_position_elements: bool = False, fixed_position_nodes: list = [], iterations: int = -1):
        self.libsbmlnetwork.autolayout(max_num_connected_edges, reset_fixed_position_elements, fixed_position_nodes, iterations)

    def auto_style(self, max_num_connected_edges: int = 3):
        self.libsbmlnetwork.autorender(max_num_connected_edges)

    def update_reactions_curves(self):
        self.libsbmlnetwork.updateReactionCurves()

    def update_network_extents(self):
        current_width = 0
        current_height = 0

        # compartments
        for compartment_index in range(self.libsbmlnetwork.getNumCompartments()):
            compartment_id = self.libsbmlnetwork.getCompartmentId(index=compartment_index)
            for compartment_glyph_index in range(self.libsbmlnetwork.getNumCompartmentGlyphs(compartment_id=compartment_id)):
                x = self.libsbmlnetwork.getX(id=compartment_id, graphical_object_index=compartment_glyph_index)
                y = self.libsbmlnetwork.getY(id=compartment_id, graphical_object_index=compartment_glyph_index)
                width = self.libsbmlnetwork.getWidth(id=compartment_id, graphical_object_index=compartment_glyph_index)
                height = self.libsbmlnetwork.getHeight(id=compartment_id, graphical_object_index=compartment_glyph_index)
                if x + width > current_width:
                    current_width = x + width
                if y + height > current_height:
                    current_height = y + height
                # text glyphs
                for text_glyph_index in range(self.libsbmlnetwork.getNumTextGlyphs(id=compartment_id, graphical_object_index=compartment_glyph_index)):
                    x = self.libsbmlnetwork.getTextX(id=compartment_id, graphical_object_index=compartment_glyph_index, text_glyph_index=text_glyph_index)
                    y = self.libsbmlnetwork.getTextY(id=compartment_id, graphical_object_index=compartment_glyph_index, text_glyph_index=text_glyph_index)
                    width = self.libsbmlnetwork.getTextWidth(id=compartment_id, graphical_object_index=compartment_glyph_index, text_glyph_index=text_glyph_index)
                    height = self.libsbmlnetwork.getTextHeight(id=compartment_id, graphical_object_index=compartment_glyph_index, text_glyph_index=text_glyph_index)
                    if x + width > current_width:
                        current_width = x + width
                    if y + height > current_height:
                        current_height = y + height

        # species
        for species_index in range(self.libsbmlnetwork.getNumSpecies()):
            species_id = self.libsbmlnetwork.getSpeciesId(index=species_index)
            for species_glyph_index in range(self.libsbmlnetwork.getNumSpeciesGlyphs(species_id=species_id)):
                x = self.libsbmlnetwork.getX(id=species_id, graphical_object_index=species_glyph_index)
                y = self.libsbmlnetwork.getY(id=species_id, graphical_object_index=species_glyph_index)
                width = self.libsbmlnetwork.getWidth(id=species_id, graphical_object_index=species_glyph_index)
                height = self.libsbmlnetwork.getHeight(id=species_id, graphical_object_index=species_glyph_index)
                if x + width > current_width:
                    current_width = x + width
                if y + height > current_height:
                    current_height = y + height
                # text glyphs
                for text_glyph_index in range(self.libsbmlnetwork.getNumTextGlyphs(id=species_id, graphical_object_index=species_glyph_index)):
                    x = self.libsbmlnetwork.getTextX(id=species_id, graphical_object_index=species_glyph_index, text_glyph_index=text_glyph_index)
                    y = self.libsbmlnetwork.getTextY(id=species_id, graphical_object_index=species_glyph_index, text_glyph_index=text_glyph_index)
                    width = self.libsbmlnetwork.getTextWidth(id=species_id, graphical_object_index=species_glyph_index, text_glyph_index=text_glyph_index)
                    height = self.libsbmlnetwork.getTextHeight(id=species_id, graphical_object_index=species_glyph_index, text_glyph_index=text_glyph_index)
                    if x + width > current_width:
                        current_width = x + width
                    if y + height > current_height:
                        current_height = y + height

        # reactions
        for reaction_index in range(self.libsbmlnetwork.getNumReactions()):
            reaction_id = self.libsbmlnetwork.getReactionId(index=reaction_index)
            for reaction_glyph_index in range(self.libsbmlnetwork.getNumReactionGlyphs(reaction_id=reaction_id)):
                x = self.libsbmlnetwork.getX(id=reaction_id, graphical_object_index=reaction_glyph_index)
                y = self.libsbmlnetwork.getY(id=reaction_id, graphical_object_index=reaction_glyph_index)
                width = self.libsbmlnetwork.getWidth(id=reaction_id, graphical_object_index=reaction_glyph_index)
                height = self.libsbmlnetwork.getHeight(id=reaction_id, graphical_object_index=reaction_glyph_index)
                if x + width > current_width:
                    current_width = x + width
                if y + height > current_height:
                    current_height = y + height
                # text glyphs
                for text_glyph_index in range(self.libsbmlnetwork.getNumTextGlyphs(id=reaction_id, graphical_object_index=reaction_glyph_index)):
                    x = self.libsbmlnetwork.getTextX(id=reaction_id, graphical_object_index=reaction_glyph_index, text_glyph_index=text_glyph_index)
                    y = self.libsbmlnetwork.getTextY(id=reaction_id, graphical_object_index=reaction_glyph_index, text_glyph_index=text_glyph_index)
                    width = self.libsbmlnetwork.getTextWidth(id=reaction_id, graphical_object_index=reaction_glyph_index, text_glyph_index=text_glyph_index)
                    height = self.libsbmlnetwork.getTextHeight(id=reaction_id, graphical_object_index=reaction_glyph_index, text_glyph_index=text_glyph_index)
                    if x + width > current_width:
                        current_width = x + width
                    if y + height > current_height:
                        current_height = y + height
                # empty species
                for species_reference_index in range(self.libsbmlnetwork.getNumSpeciesReferences(reaction_id=reaction_id, reaction_glyph_index=reaction_glyph_index)):
                    if self.libsbmlnetwork.isSetSpeciesReferenceEmptySpeciesGlyph(reaction_id=reaction_id, reaction_glyph_index=reaction_glyph_index, species_reference_index=species_reference_index):
                        empty_species_id = self.libsbmlnetwork.getSpeciesReferenceEmptySpeciesGlyphId(reaction_id=reaction_id, reaction_glyph_index=reaction_glyph_index, species_reference_index=species_reference_index)
                        x = self.libsbmlnetwork.getX(id=empty_species_id, graphical_object_index=0)
                        y = self.libsbmlnetwork.getY(id=empty_species_id, graphical_object_index=0)
                        width = self.libsbmlnetwork.getWidth(id=empty_species_id, graphical_object_index=0)
                        height = self.libsbmlnetwork.getHeight(id=empty_species_id, graphical_object_index=0)
                        if x + width > current_width:
                            current_width = x + width
                        if y + height > current_height:
                            current_height = y + height

        # independent text glyphs
        for independent_text_glyph_index in range(self.libsbmlnetwork.getNumAllIndependentTextGlyphs()):
            independent_text_glyph_id = self.libsbmlnetwork.getIndependentTextGlyphId(independent_text_glyph_index=independent_text_glyph_index)
            x = self.libsbmlnetwork.getTextX(id=independent_text_glyph_id, graphical_object_index=0)
            y = self.libsbmlnetwork.getTextY(id=independent_text_glyph_id, graphical_object_index=0)
            width = self.libsbmlnetwork.getTextWidth(id=independent_text_glyph_id, graphical_object_index=0)
            height = self.libsbmlnetwork.getTextHeight(id=independent_text_glyph_id, graphical_object_index=0)
            if x + width > current_width:
                current_width = x + width
            if y + height > current_height:
                current_height = y + height

        # additional graphical objects
        for graphical_object_index in range(self.libsbmlnetwork.getNumAllAdditionalGraphicalObjects()):
            graphical_object_id = self.libsbmlnetwork.getAdditionalGraphicalObjectId(additional_graphical_object_index=graphical_object_index)
            x = self.libsbmlnetwork.getX(id=graphical_object_id, graphical_object_index=0)
            y = self.libsbmlnetwork.getY(id=graphical_object_id, graphical_object_index=0)
            width = self.libsbmlnetwork.getWidth(id=graphical_object_id, graphical_object_index=0)
            height = self.libsbmlnetwork.getHeight(id=graphical_object_id, graphical_object_index=0)
            if x + width > current_width:
                current_width = x + width
            if y + height > current_height:
                current_height = y + height

            # text glyphs
            for text_glyph_index in range(self.libsbmlnetwork.getNumTextGlyphs(id=graphical_object_id, graphical_object_index=0)):
                x = self.libsbmlnetwork.getTextX(id=graphical_object_id, graphical_object_index=0, text_glyph_index=text_glyph_index)
                y = self.libsbmlnetwork.getTextY(id=graphical_object_id, graphical_object_index=0, text_glyph_index=text_glyph_index)
                width = self.libsbmlnetwork.getTextWidth(id=graphical_object_id, graphical_object_index=0, text_glyph_index=text_glyph_index)
                height = self.libsbmlnetwork.getTextHeight(id=graphical_object_id, graphical_object_index=0, text_glyph_index=text_glyph_index)
                if x + width > current_width:
                    current_width = x + width
                if y + height > current_height:
                    current_height = y + height

        if self.libsbmlnetwork.getNumAllCompartmentGlyphs() == 1:
            sole_compartment = self.get_compartment()
            compartment_width = current_width - sole_compartment.get_position()[0]
            compartment_height = current_height - sole_compartment.get_position()[1]
            fluxes_color_bar = self.get_color_bar("fluxes")
            if fluxes_color_bar:
                compartment_width -= fluxes_color_bar.get_horizontal_extent()
            concentration_color_bar = self.get_color_bar("concentrations")
            if concentration_color_bar:
                compartment_width -= concentration_color_bar.get_horizontal_extent()

            sole_compartment.set_size((compartment_width, compartment_height))

        self.libsbmlnetwork.setCanvasWidth(current_width)
        self.libsbmlnetwork.setCanvasHeight(current_height)

    def get_settings(self):
        return self.settings

    def populate_settings(self):
        self.libsbmlnetwork.enableDisplayCompartmentsTextLabel(self.settings.compartment_labels)
        self.libsbmlnetwork.enableDisplaySpeciesTextLabel(self.settings.species_labels)
        self.libsbmlnetwork.enableDisplayReactionsTextLabel(self.settings.reaction_labels)
        if self.settings.label == "name":
            self.libsbmlnetwork.setUseNameAsTextLabel(True)
        else:
            self.libsbmlnetwork.setUseNameAsTextLabel(False)
        self.libsbmlnetwork.setStoichiometricSpeciesReference(self.settings.stoichiometric_curves)

    #ToDo: Implement error_log method

    def get_version(self):
        return self.libsbmlnetwork.getVersion()

    @property
    def version(self):
        return self.get_version()


instance = SBMLNetwork()


def load(sbml: str):
    """
    Loads the SBML model.

    :param sbml: The SBML model.
    :return: an instance of the SBMLNetwork class.
    """
    instance.load(sbml)
    return instance


version = instance.get_version()
settings = instance.get_settings()
