"""
Pay to delegated conditions

In this puzzle program, the solution must be a signed list of conditions, which
is returned literally.
"""


from achi.types.blockchain_format.program import Program

from .load_alvm import load_alvm

MOD = load_alvm("p2_delegated_conditions.alvm")


def puzzle_for_pk(public_key: Program) -> Program:
    return MOD.curry(public_key)


def solution_for_conditions(conditions: Program) -> Program:
    return conditions.to([conditions])
