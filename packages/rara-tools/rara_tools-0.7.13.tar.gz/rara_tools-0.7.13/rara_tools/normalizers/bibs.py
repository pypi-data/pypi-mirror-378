from pymarc import (Field, Subfield, Record)
from typing import List, Optional

from rara_tools.constants import EMPTY_INDICATORS
from rara_tools.normalizers.viaf import VIAFRecord
from rara_tools.normalizers import RecordNormalizer

from typing import List


class BibRecordNormalizer(RecordNormalizer):
    """ Normalize bib records. """

    def __init__(self, linking_results: List[dict] = [], sierra_data: List[dict] = [],
                 ALLOW_EDIT_FIELDS: List[str] = ["008", "925"],
                 REPEATABLE_FIELDS: List[str] = ["667"]):
        super().__init__(linking_results, sierra_data)
        self.DEFAULT_LEADER = "00399nz  a2200145n  4500" # must be 24 digits
        self.ALLOW_EDIT_FIELDS = ALLOW_EDIT_FIELDS
        self.REPEATABLE_FIELDS = REPEATABLE_FIELDS
        
        self.records_extra_data = []
        self.sierra_data = sierra_data
        self.records = self._setup_records(linking_results, sierra_data)

    def _normalize_sierra(self, record: Record) -> Record:
        
        suffix_008 = "|||aznnnaabn          || |||      "
        
        fields = [
            Field(
                tag="008",
                data=f"{self.current_timestamp()}{suffix_008}"
            ),
        ]

        self._add_fields_to_record(record, fields)
        
    def _include_name_variations(self, record: Record, viaf_record: VIAFRecord) -> None:
        """ Include name variations from VIAF record as 400|t fields """
        
        if not viaf_record or not viaf_record.name_variations:
            return
        
        existing_name_variations = record.get_fields("400")
        existing_variations = [sf.value for field in existing_name_variations for sf in field.get_subfields("t")]
        
        fields = []
        
        for variation in viaf_record.name_variations:
            if variation not in existing_variations:
                fields.append(
                    Field(
                        tag="400",
                        indicators=EMPTY_INDICATORS,
                        subfields=[
                            Subfield("t", variation)
                        ]
                    )
                )
        
        self._add_fields_to_record(record, fields)
        
    def _add_author(self, record: Record, viaf_record: Optional[VIAFRecord], original_entity: str) -> Optional[Field]:
        if record.get("100") or record.get("110") or record.get("111"):
            return record

        type_map = {
            "Personal": "100",
            "Corporate": "110",
            "Collective": "111"
        }
        
        tag = type_map.get(getattr(viaf_record, "name_type", None), "100")
        title = getattr(viaf_record, "name", None) or original_entity

        fields = [Field(tag=tag, indicators=EMPTY_INDICATORS, subfields=[Subfield("t", title)])]
        
        self._add_fields_to_record(record, fields)
        
        if viaf_record:
            self._include_name_variations(record, viaf_record)

    def _normalize_viaf(self, record: Record, viaf_record: VIAFRecord, original_entity: str) -> None:
        
        if not viaf_record:
            # viaf record not found, include original entity as 100|t
            self._add_author(record, viaf_record=None, original_entity=original_entity)
            return record

        viaf_id = viaf_record.viaf_id
        fields = [
            Field(
                tag="035",
                indicators=EMPTY_INDICATORS,
                subfields=[
                    Subfield("a", viaf_id)
                ]
            )
        ]

        self._add_fields_to_record(record, fields)
        self._add_author(record, viaf_record, original_entity=original_entity)

    def _normalize_record(self, record: Record, sierraID: str,
                          viaf_record: VIAFRecord, is_editing_existing_record: bool, original_entity: str) -> Record:

        self._normalize_sierra(record)
        self._normalize_viaf(record, viaf_record, original_entity=original_entity)

        return record
