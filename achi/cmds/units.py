from typing import Dict

# The rest of the codebase uses stens everywhere. Only uses these units
# for user facing interfaces
units: Dict[str, int] = {
    "achi": 10 ** 9,  # 1 achi (XACH) is 1,000,000,000 sten (1 Billion)
    "sten:": 1,
    "colouredcoin": 10 ** 3,  # 1 coloured coin is 1000 colouredcoin stens
}
