import uuid
from dis import Instruction
from typing import Any, Optional

from .actions import *
from .utils import strip_none


class State:
    uniqid = str(uuid.uuid4())



class Turing:
    alphabet: list[Any]
    table: dict[State, dict[Any, list]]
    state: State

    def __init__(self, alphabet: list[Any], table: dict[State, dict[Any, list]], state: State = None) -> None:
        self.table = table
        self.alphabet = alphabet
        self.state = list(self.table.keys())[0] if state is None else state

    def determine_instruction(self, state: State, value: Any) -> Optional[list]:
        base = self.table[state]
        for specimen in base:
            if value == specimen or (type(specimen) == tuple and value in specimen):
                return base[specimen]
        return None


class Tape:
    tape: list[Any]
    lambdas_from: int
    lambdas_to: int
    initial_pos: int = 0

    def __init__(self, tape: list[Any]) -> None:
        self.tape = tape
        self.lambdas_to = 0
        self.lambdas_from = len(tape)

    def __str__(self) -> str:
        return f"<Tape: from {self.lambdas_to} to {self.lambdas_from - 1}> " + ', '.join(
            map(str, ["...", *self.tape, "..."]))

    def get(self, position: int) -> Any:
        if position >= self.lambdas_from or position < self.lambdas_to:
            return None
        return self.tape[position + self.initial_pos]

    def set(self, position: int, value: Any) -> Any:
        if position >= self.lambdas_from:
            for i in range(self.lambdas_from, position):
                self.tape.append(None)
            self.tape.append(value)
            self.lambdas_from = position
        elif position < self.lambdas_to:
            for i in range(self.lambdas_to - 1, position, -1):
                self.tape.insert(0, None)
            self.tape.insert(0, value)
            self.lambdas_to = position
            self.initial_pos -= position
        else:
            self.tape[position] = value

        return value

    def run(self, turing: Turing, index: int) -> None:
        current = index
        iterations = 0

        while iterations < 100000:
            value = self.get(current)
            instruction: list = turing.determine_instruction(turing.state, value)

            if instruction is None:
                raise RuntimeError(f"No matching instruction for {value} at state {turing.state.uniqid}")

            new_value = instruction[0]
            move = instruction[1]
            new_state = instruction[2] if len(instruction) > 2 else turing.state

            self.set(current, new_value)

            if move == L:
                current -= 1
            elif move == R:
                current += 1
            elif move == N:
                pass
            elif move == S:
                break

            turing.state = new_state

            iterations += 1
        else:
            raise RuntimeError("Iterations limit reached. Looks like your program will continue to infinity.")

        self.clean()

    def clean(self):
        start = self.lambdas_to
        end = self.lambdas_from
        while self.get(start) is None and start < end:
            self.initial_pos -= 1
            start += 1
        while self.get(end - 1) is None and start < end:
            end -= 1

        self.lambdas_to = start
        self.lambdas_from = end
        self.tape = strip_none(self.tape)



def States(n: int) -> tuple[State, ...]:
    return tuple(State() for _ in range(n))
