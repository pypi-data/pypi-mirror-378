import uuid
from typing import Any, Optional

from .actions import *
from .struct import TapeArray
from .utils import strip_none


class State:
    uniqid = str(uuid.uuid4())


class Turing:
    alphabet: list[Any]
    table: dict[State, dict[Any, list]]
    initial_state: State
    state: State
    iteration_limit: int

    def __init__(self,
        alphabet: list[Any],
        table: dict[State, dict[Any, list]],
        state: State = None,
        iteration_limit: int = 100000
    ) -> None:
        self.table = table
        self.alphabet = alphabet
        self.initial_state = list(self.table.keys())[0] if state is None else state
        self.state = self.initial_state
        self.iteration_limit = iteration_limit

    def determine_instruction(self, state: State, value: Any) -> Optional[list]:
        base = self.table[state]
        for specimen in base:
            if value == specimen or (type(specimen) == tuple and value in specimen):
                return base[specimen]
        return None


class Tape:
    tape: TapeArray
    initial_pos: int = 0

    def __init__(self,
        tape: list[Any] | str,
        process_as = int,
    ) -> None:
        self.tape = TapeArray(None)

        for i, item in enumerate(tape):
            self.tape[i] = process_as(item)

    def __str__(self) -> str:
        return self.tape.__repr__()

    def get(self, position: int) -> Any:
        return self.tape[position]

    def set(self, position: int, value: Any) -> Any:
        self.tape[position] = value

        return value

    def run(self, turing: Turing, index: int) -> None:
        current = index
        iterations = 0
        state = turing.state

        while iterations < turing.iteration_limit:
            value = self.get(current)
            instruction: list = turing.determine_instruction(state, value)

            if instruction is None:
                raise RuntimeError(f"No matching instruction for {value} <{type(value).__name__}>")

            new_value = instruction[0]
            move = instruction[1]
            new_state = instruction[2] if len(instruction) > 2 else state

            if not (value is None and new_value is None) and not new_value == Let:
                self.set(current, new_value)

            if move == L:
                current -= 1
            elif move == R:
                current += 1
            elif move == N:
                pass
            elif move == S:
                break

            state = new_state

            iterations += 1
        else:
            raise RuntimeError("Iterations limit reached. Looks like your program will continue to infinity.")

    def run_at_start(self, turing: Turing, offset: int = 0):
        self.run(turing, self.tape.start + offset)

    def run_at_end(self, turing: Turing, offset: int = 0):
        self.run(turing, self.tape.end + offset)




def States(n: int) -> tuple[State, ...]:
    return tuple(State() for _ in range(n))
