"""Handle GEDCOM individual records and import them into the Gramps database."""

from typing import List

from gedcom7 import const as g7const
from gedcom7 import grammar as g7grammar
from gedcom7 import types as g7types
from gramps.gen.lib import (
    Attribute,
    AttributeType,
    EventRef,
    EventType,
    Name,
    NameType,
    Person,
    Surname,
)
from gramps.gen.lib.primaryobj import BasicPrimaryObject

from . import util
from .event import handle_event
from .citation import handle_citation
from .settings import ImportSettings

GENDER_MAP = {
    "M": Person.MALE,
    "F": Person.FEMALE,
    "U": Person.UNKNOWN,
    "X": Person.OTHER,
}

NAME_TYPE_MAP = {
    "AKA": NameType(NameType.AKA),
    "BIRTH": NameType(NameType.BIRTH),
    "MARR": NameType(NameType.MARRIED),
    "OTHER": NameType(NameType.CUSTOM),
}

EVENT_TYPE_MAP = {
    g7const.ADOP: EventType.ADOPT,
    g7const.BAPM: EventType.BAPTISM,
    g7const.BARM: EventType.BAR_MITZVAH,
    g7const.BASM: EventType.BAS_MITZVAH,
    g7const.BIRT: EventType.BIRTH,
    g7const.BLES: EventType.BLESS,
    g7const.BURI: EventType.BURIAL,
    g7const.CENS: EventType.CENSUS,
    g7const.CHR: EventType.CHRISTEN,
    g7const.CHRA: EventType.ADULT_CHRISTEN,
    g7const.CONF: EventType.CONFIRMATION,
    g7const.CREM: EventType.CREMATION,
    g7const.DEAT: EventType.DEATH,
    g7const.EMIG: EventType.EMIGRATION,
    g7const.FCOM: EventType.FIRST_COMMUN,
    g7const.GRAD: EventType.GRADUATION,
    g7const.IMMI: EventType.IMMIGRATION,
    g7const.NATU: EventType.NATURALIZATION,
    g7const.ORDN: EventType.ORDINATION,
    g7const.PROB: EventType.PROBATE,
    g7const.RETI: EventType.RETIREMENT,
    g7const.WILL: EventType.WILL,
    g7const.EVEN: EventType.CUSTOM,
}


def handle_individual(
    structure: g7types.GedcomStructure,
    xref_handle_map: dict[str, str],
    settings: ImportSettings,
) -> List[BasicPrimaryObject]:
    """Handle an individual record and convert it to Gramps objects.

    Args:
        structure: The GEDCOM note structure to handle.
        xref_handle_map: A map of XREFs to Gramps handles.

    Returns:
        A list of Gramps objects created from the GEDCOM structure.
    """
    person = Person()
    objects = []
    for child in structure.children:
        if child.tag == g7const.RESN:
            util.set_privacy_on_object(resn_structure=child, obj=person)
        elif child.tag == g7const.SEX:
            assert isinstance(child.value, str), "Expected SEX to be a string"
            try:
                gender = GENDER_MAP[child.value]
                person.set_gender(gender)
            except KeyError:
                raise ValueError(f"SEX value '{child.value}' is not valid")
        elif child.tag == g7const.NAME:
            name, other_objects = handle_name(child, xref_handle_map=xref_handle_map)
            objects.extend(other_objects)
            if person.primary_name.is_empty():
                person.set_primary_name(name)
            else:
                person.add_alternate_name(name)
        # TODO handle attributes
        # TODO handle SUBM
        # TODO handle associations
        # TODO handle ALIA
        # TODO handle ANCI
        # TODO handle DESI
        elif child.tag == g7const.EXID:
            util.handle_external_id(child, person)
        elif child.tag == g7const.REFN:
            util.handle_external_id(child, person)
        elif child.tag == g7const.UID:
            util.add_uid_to_object(child, person)
        elif child.tag == g7const.FAMC and child.pointer != g7grammar.voidptr:
            family_handle = xref_handle_map.get(child.pointer)
            if not family_handle:
                raise ValueError(f"Family {child.pointer} not found")
            person.add_parent_family_handle(family_handle)
            # TODO child ref type should be handled in the family!
            # TODO handle FAMC PHRASE
        elif child.tag == g7const.FAMS and child.pointer != g7grammar.voidptr:
            family_handle = xref_handle_map.get(child.pointer)
            if not family_handle:
                raise ValueError(f"Family {child.pointer} not found")
            person.add_family_handle(family_handle)
            # TODO handle FAMS PHRASE
        elif child.tag == g7const.SNOTE and child.pointer != g7grammar.voidptr:
            try:
                note_handle = xref_handle_map[child.pointer]
            except KeyError:
                raise ValueError(f"Shared note {child.pointer} not found")
            person.add_note(note_handle)
        elif child.tag == g7const.NOTE:
            person, note = util.add_note_to_object(child, person)
            objects.append(note)
        elif child.tag == g7const.OBJE:
            person = util.add_media_ref_to_object(child, person, xref_handle_map)
        elif child.tag in EVENT_TYPE_MAP:
            event, other_objects = handle_event(
                child,
                xref_handle_map=xref_handle_map,
                event_type_map=EVENT_TYPE_MAP,
                settings=settings,
            )
            objects.extend(other_objects)
            event_ref = EventRef()
            event_ref.ref = event.handle
            person.add_event_ref(event_ref)
            objects.append(event)
        elif child.tag == g7const.SOUR:
            citation, other_objects = handle_citation(
                child,
                xref_handle_map=xref_handle_map,
                settings=settings,
            )
            objects.extend(other_objects)
            person.add_citation(citation.handle)
            objects.append(citation)
    person = util.add_ids(person, structure=structure, xref_handle_map=xref_handle_map)
    util.set_change_date(structure=structure, obj=person)
    objects.append(person)
    return objects


def handle_name(
    structure: g7types.GedcomStructure, xref_handle_map: dict[str, str]
) -> tuple[Name, list[BasicPrimaryObject]]:
    """Convert a GEDCOM structure to a Gramps Name object.

    Args:
        structure: The GEDCOM structure containing the name data.

    Returns:
        A tuple containing the Gramps Name object and a list of additional objects created.
    """
    name = Name()
    surname = Surname()
    objects = []
    personal_name = structure.value
    assert isinstance(
        personal_name, g7types.PersonalName
    ), "Expected structure value to be a PersonalName"
    for child in structure.children:
        if child.tag == g7const.TYPE:
            assert isinstance(child.value, str), "Expected TYPE value to be a string"
            gramps_name_type_value = NAME_TYPE_MAP.get(child.value, NameType.CUSTOM)
            gramps_name_type = NameType(gramps_name_type_value)
            if gramps_name_type_value == NameType.CUSTOM:
                gramps_name_type.string = child.value
            name.set_type(gramps_name_type)
        elif child.tag == g7const.NPFX:
            assert isinstance(child.value, str), "Expected NPFX value to be a string"
            name.set_title(child.value)
        elif child.tag == g7const.GIVN:
            assert isinstance(child.value, str), "Expected GIVN value to be a string"
            name.set_first_name(child.value)
        elif child.tag == g7const.NICK:
            assert isinstance(child.value, str), "Expected NICK value to be a string"
            name.set_nick_name(child.value)
        elif child.tag == g7const.SPFX:
            assert isinstance(child.value, str), "Expected SPFX value to be a string"
            surname.set_prefix(child.value)
        elif child.tag == g7const.SURN:
            assert isinstance(child.value, str), "Expected SURN value to be a string"
            surname.set_surname(child.value)
        elif child.tag == g7const.NSFX:
            assert isinstance(child.value, str), "Expected NSFX value to be a string"
            name.set_suffix(child.value)
        elif child.tag == g7const.SNOTE and child.pointer != g7grammar.voidptr:
            try:
                note_handle = xref_handle_map[child.pointer]
            except KeyError:
                raise ValueError(f"Shared note {child.pointer} not found")
            name.add_note(note_handle)
        elif child.tag == g7const.NOTE:
            name, note = util.add_note_to_object(child, name)
            objects.append(note)
    # if name parts are not given, use the personal name parts
    if not name.first_name and personal_name.given:
        name.set_first_name(personal_name.given)
    if not surname.surname and personal_name.surname:
        surname.set_surname(personal_name.surname)
    if not name.suffix and personal_name.suffix:
        name.set_suffix(personal_name.suffix)
    if not surname.is_empty():
        name.add_surname(surname)
    # last resort - only single string, no surname markers - take as first name only
    if name.is_empty():
        name.set_first_name(personal_name.fullname)
    return name, objects
