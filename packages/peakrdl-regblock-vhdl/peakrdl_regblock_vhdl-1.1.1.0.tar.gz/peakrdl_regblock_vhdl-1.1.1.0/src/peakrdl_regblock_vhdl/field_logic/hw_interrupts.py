from typing import TYPE_CHECKING, List

from systemrdl.rdltypes import InterruptType

from .bases import NextStateConditional
from ..vhdl_int import VhdlInt

if TYPE_CHECKING:
    from systemrdl.node import FieldNode


class Sticky(NextStateConditional):
    """
    Normal multi-bit sticky
    """
    comment = "multi-bit sticky"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('sticky')
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        R = self.exp.field_logic.get_storage_identifier(field)
        zero = VhdlInt.bit_string(0, field.width)
        return f"to_std_logic({R} = {zero}) and or_reduce({I})"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        I = self.exp.hwif.get_input_identifier(field)
        return [
            f"next_c := {I};",
            "load_next_c := '1';",
        ]


class Stickybit(NextStateConditional):
    """
    Normal stickybit
    """
    comment = "stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
            and field.get_property('intr type') in {None, InterruptType.level}
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        F = self.exp.hwif.get_input_identifier(field)
        if field.width == 1:
            return str(F)
        else:
            return f"or_reduce({F})"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        if field.width == 1:
            return [
                "next_c := '1';",
                "load_next_c := '1';",
            ]
        else:
            I = self.exp.hwif.get_input_identifier(field)
            R = self.exp.field_logic.get_storage_identifier(field)
            return [
                f"next_c := {R} or {I};",
                "load_next_c := '1';",
            ]

class PosedgeStickybit(NextStateConditional):
    """
    Positive edge stickybit
    """
    comment = "posedge stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.posedge
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        return f"or_reduce(not {Iq} and {I})"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        if field.width == 1:
            return [
                "next_c := '1';",
                "load_next_c := '1';",
            ]
        else:
            I = self.exp.hwif.get_input_identifier(field)
            Iq = self.exp.field_logic.get_next_q_identifier(field)
            R = self.exp.field_logic.get_storage_identifier(field)
            return [
                f"next_c := {R} or (not {Iq} and {I});",
                "load_next_c := '1';",
            ]

class NegedgeStickybit(NextStateConditional):
    """
    Negative edge stickybit
    """
    comment = "negedge stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.negedge
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        return f"or_reduce({Iq} and not {I})"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        if field.width == 1:
            return [
                "next_c := '1';",
                "load_next_c := '1';",
            ]
        else:
            I = self.exp.hwif.get_input_identifier(field)
            Iq = self.exp.field_logic.get_next_q_identifier(field)
            R = self.exp.field_logic.get_storage_identifier(field)
            return [
                f"next_c := {R} or ({Iq} and not {I});",
                "load_next_c := '1';",
            ]

class BothedgeStickybit(NextStateConditional):
    """
    edge-sensitive stickybit
    """
    comment = "bothedge stickybit"
    def is_match(self, field: 'FieldNode') -> bool:
        return (
            field.is_hw_writable
            and field.get_property('stickybit')
            and field.get_property('intr type') == InterruptType.bothedge
        )

    def get_predicate(self, field: 'FieldNode') -> str:
        I = self.exp.hwif.get_input_identifier(field)
        Iq = self.exp.field_logic.get_next_q_identifier(field)
        return f"or_reduce({Iq} xor {I})"

    def get_assignments(self, field: 'FieldNode') -> List[str]:
        if field.width == 1:
            return [
                "next_c := '1';",
                "load_next_c := '1';",
            ]
        else:
            I = self.exp.hwif.get_input_identifier(field)
            Iq = self.exp.field_logic.get_next_q_identifier(field)
            R = self.exp.field_logic.get_storage_identifier(field)
            return [
                f"next_c := {R} or ({Iq} xor {I});",
                "load_next_c := '1';",
            ]
