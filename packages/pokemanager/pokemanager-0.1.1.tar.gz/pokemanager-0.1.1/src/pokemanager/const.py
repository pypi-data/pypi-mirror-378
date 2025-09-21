"""."""

from enum import IntEnum, auto
from typing import Literal, cast

TYPE = Literal[
    "Normal",
    "Fire",
    "Water",
    "Electric",
    "Grass",
    "Ice",
    "Fighting",
    "Poison",
    "Ground",
    "Flying",
    "Psychic",
    "Bug",
    "Rock",
    "Ghost",
    "Dragon",
    "Dark",
    "Steel",
    "Fairy",
]

DUAL = Literal[
    "Normal",
    "Normal_Fire",
    "Normal_Water",
    "Normal_Electric",
    "Normal_Grass",
    "Normal_Ice",
    "Normal_Fighting",
    "Normal_Poison",
    "Normal_Ground",
    "Normal_Flying",
    "Normal_Psychic",
    "Normal_Bug",
    "Normal_Rock",
    "Normal_Ghost",
    "Normal_Dragon",
    "Normal_Dark",
    "Normal_Steel",
    "Normal_Fairy",
    "Fire",
    "Fire_Water",
    "Fire_Electric",
    "Fire_Grass",
    "Fire_Ice",
    "Fire_Fighting",
    "Fire_Poison",
    "Fire_Ground",
    "Fire_Flying",
    "Fire_Psychic",
    "Fire_Bug",
    "Fire_Rock",
    "Fire_Ghost",
    "Fire_Dragon",
    "Fire_Dark",
    "Fire_Steel",
    "Fire_Fairy",
    "Water",
    "Water_Electric",
    "Water_Grass",
    "Water_Ice",
    "Water_Fighting",
    "Water_Poison",
    "Water_Ground",
    "Water_Flying",
    "Water_Psychic",
    "Water_Bug",
    "Water_Rock",
    "Water_Ghost",
    "Water_Dragon",
    "Water_Dark",
    "Water_Steel",
    "Water_Fairy",
    "Electric",
    "Electric_Grass",
    "Electric_Ice",
    "Electric_Fighting",
    "Electric_Poison",
    "Electric_Ground",
    "Electric_Flying",
    "Electric_Psychic",
    "Electric_Bug",
    "Electric_Rock",
    "Electric_Ghost",
    "Electric_Dragon",
    "Electric_Dark",
    "Electric_Steel",
    "Electric_Fairy",
    "Grass",
    "Grass_Ice",
    "Grass_Fighting",
    "Grass_Poison",
    "Grass_Ground",
    "Grass_Flying",
    "Grass_Psychic",
    "Grass_Bug",
    "Grass_Rock",
    "Grass_Ghost",
    "Grass_Dragon",
    "Grass_Dark",
    "Grass_Steel",
    "Grass_Fairy",
    "Ice",
    "Ice_Fighting",
    "Ice_Poison",
    "Ice_Ground",
    "Ice_Flying",
    "Ice_Psychic",
    "Ice_Bug",
    "Ice_Rock",
    "Ice_Ghost",
    "Ice_Dragon",
    "Ice_Dark",
    "Ice_Steel",
    "Ice_Fairy",
    "Fighting",
    "Fighting_Poison",
    "Fighting_Ground",
    "Fighting_Flying",
    "Fighting_Psychic",
    "Fighting_Bug",
    "Fighting_Rock",
    "Fighting_Ghost",
    "Fighting_Dragon",
    "Fighting_Dark",
    "Fighting_Steel",
    "Fighting_Fairy",
    "Poison",
    "Poison_Ground",
    "Poison_Flying",
    "Poison_Psychic",
    "Poison_Bug",
    "Poison_Rock",
    "Poison_Ghost",
    "Poison_Dragon",
    "Poison_Dark",
    "Poison_Steel",
    "Poison_Fairy",
    "Ground",
    "Ground_Flying",
    "Ground_Psychic",
    "Ground_Bug",
    "Ground_Rock",
    "Ground_Ghost",
    "Ground_Dragon",
    "Ground_Dark",
    "Ground_Steel",
    "Ground_Fairy",
    "Flying",
    "Flying_Psychic",
    "Flying_Bug",
    "Flying_Rock",
    "Flying_Ghost",
    "Flying_Dragon",
    "Flying_Dark",
    "Flying_Steel",
    "Flying_Fairy",
    "Psychic",
    "Psychic_Bug",
    "Psychic_Rock",
    "Psychic_Ghost",
    "Psychic_Dragon",
    "Psychic_Dark",
    "Psychic_Steel",
    "Psychic_Fairy",
    "Bug",
    "Bug_Rock",
    "Bug_Ghost",
    "Bug_Dragon",
    "Bug_Dark",
    "Bug_Steel",
    "Bug_Fairy",
    "Rock",
    "Rock_Ghost",
    "Rock_Dragon",
    "Rock_Dark",
    "Rock_Steel",
    "Rock_Fairy",
    "Ghost",
    "Ghost_Dragon",
    "Ghost_Dark",
    "Ghost_Steel",
    "Ghost_Fairy",
    "Dragon",
    "Dragon_Dark",
    "Dragon_Steel",
    "Dragon_Fairy",
    "Dark",
    "Dark_Steel",
    "Dark_Fairy",
    "Steel",
    "Steel_Fairy",
    "Fairy",
]


class Type(IntEnum):
    """A single type."""

    Normal = 0
    Fire = auto()
    Water = auto()
    Electric = auto()
    Grass = auto()
    Ice = auto()
    Fighting = auto()
    Poison = auto()
    Ground = auto()
    Flying = auto()
    Psychic = auto()
    Bug = auto()
    Rock = auto()
    Ghost = auto()
    Dragon = auto()
    Dark = auto()
    Steel = auto()
    Fairy = auto()


class Dual(IntEnum):
    """A dual type, or single type if both types are the same."""

    Normal = 0
    Normal_Normal = 0

    Normal_Fire = 1
    Fire_Normal = 1

    Normal_Water = 2
    Water_Normal = 2

    Normal_Electric = 3
    Electric_Normal = 3

    Normal_Grass = 4
    Grass_Normal = 4

    Normal_Ice = 5
    Ice_Normal = 5

    Normal_Fighting = 6
    Fighting_Normal = 6

    Normal_Poison = 7
    Poison_Normal = 7

    Normal_Ground = 8
    Ground_Normal = 8

    Normal_Flying = 9
    Flying_Normal = 9

    Normal_Psychic = 10
    Psychic_Normal = 10

    Normal_Bug = 11
    Bug_Normal = 11

    Normal_Rock = 12
    Rock_Normal = 12

    Normal_Ghost = 13
    Ghost_Normal = 13

    Normal_Dragon = 14
    Dragon_Normal = 14

    Normal_Dark = 15
    Dark_Normal = 15

    Normal_Steel = 16
    Steel_Normal = 16

    Normal_Fairy = 17
    Fairy_Normal = 17

    Fire = 18
    Fire_Fire = 18

    Fire_Water = 19
    Water_Fire = 19

    Fire_Electric = 20
    Electric_Fire = 20

    Fire_Grass = 21
    Grass_Fire = 21

    Fire_Ice = 22
    Ice_Fire = 22

    Fire_Fighting = 23
    Fighting_Fire = 23

    Fire_Poison = 24
    Poison_Fire = 24

    Fire_Ground = 25
    Ground_Fire = 25

    Fire_Flying = 26
    Flying_Fire = 26

    Fire_Psychic = 27
    Psychic_Fire = 27

    Fire_Bug = 28
    Bug_Fire = 28

    Fire_Rock = 29
    Rock_Fire = 29

    Fire_Ghost = 30
    Ghost_Fire = 30

    Fire_Dragon = 31
    Dragon_Fire = 31

    Fire_Dark = 32
    Dark_Fire = 32

    Fire_Steel = 33
    Steel_Fire = 33

    Fire_Fairy = 34
    Fairy_Fire = 34

    Water = 35
    Water_Water = 35

    Water_Electric = 36
    Electric_Water = 36

    Water_Grass = 37
    Grass_Water = 37

    Water_Ice = 38
    Ice_Water = 38

    Water_Fighting = 39
    Fighting_Water = 39

    Water_Poison = 40
    Poison_Water = 40

    Water_Ground = 41
    Ground_Water = 41

    Water_Flying = 42
    Flying_Water = 42

    Water_Psychic = 43
    Psychic_Water = 43

    Water_Bug = 44
    Bug_Water = 44

    Water_Rock = 45
    Rock_Water = 45

    Water_Ghost = 46
    Ghost_Water = 46

    Water_Dragon = 47
    Dragon_Water = 47

    Water_Dark = 48
    Dark_Water = 48

    Water_Steel = 49
    Steel_Water = 49

    Water_Fairy = 50
    Fairy_Water = 50

    Electric = 51
    Electric_Electric = 51

    Electric_Grass = 52
    Grass_Electric = 52

    Electric_Ice = 53
    Ice_Electric = 53

    Electric_Fighting = 54
    Fighting_Electric = 54

    Electric_Poison = 55
    Poison_Electric = 55

    Electric_Ground = 56
    Ground_Electric = 56

    Electric_Flying = 57
    Flying_Electric = 57

    Electric_Psychic = 58
    Psychic_Electric = 58

    Electric_Bug = 59
    Bug_Electric = 59

    Electric_Rock = 60
    Rock_Electric = 60

    Electric_Ghost = 61
    Ghost_Electric = 61

    Electric_Dragon = 62
    Dragon_Electric = 62

    Electric_Dark = 63
    Dark_Electric = 63

    Electric_Steel = 64
    Steel_Electric = 64

    Electric_Fairy = 65
    Fairy_Electric = 65

    Grass = 66
    Grass_Grass = 66

    Grass_Ice = 67
    Ice_Grass = 67

    Grass_Fighting = 68
    Fighting_Grass = 68

    Grass_Poison = 69
    Poison_Grass = 69

    Grass_Ground = 70
    Ground_Grass = 70

    Grass_Flying = 71
    Flying_Grass = 71

    Grass_Psychic = 72
    Psychic_Grass = 72

    Grass_Bug = 73
    Bug_Grass = 73

    Grass_Rock = 74
    Rock_Grass = 74

    Grass_Ghost = 75
    Ghost_Grass = 75

    Grass_Dragon = 76
    Dragon_Grass = 76

    Grass_Dark = 77
    Dark_Grass = 77

    Grass_Steel = 78
    Steel_Grass = 78

    Grass_Fairy = 79
    Fairy_Grass = 79

    Ice = 80
    Ice_Ice = 80

    Ice_Fighting = 81
    Fighting_Ice = 81

    Ice_Poison = 82
    Poison_Ice = 82

    Ice_Ground = 83
    Ground_Ice = 83

    Ice_Flying = 84
    Flying_Ice = 84

    Ice_Psychic = 85
    Psychic_Ice = 85

    Ice_Bug = 86
    Bug_Ice = 86

    Ice_Rock = 87
    Rock_Ice = 87

    Ice_Ghost = 88
    Ghost_Ice = 88

    Ice_Dragon = 89
    Dragon_Ice = 89

    Ice_Dark = 90
    Dark_Ice = 90

    Ice_Steel = 91
    Steel_Ice = 91

    Ice_Fairy = 92
    Fairy_Ice = 92

    Fighting = 93
    Fighting_Fighting = 93

    Fighting_Poison = 94
    Poison_Fighting = 94

    Fighting_Ground = 95
    Ground_Fighting = 95

    Fighting_Flying = 96
    Flying_Fighting = 96

    Fighting_Psychic = 97
    Psychic_Fighting = 97

    Fighting_Bug = 98
    Bug_Fighting = 98

    Fighting_Rock = 99
    Rock_Fighting = 99

    Fighting_Ghost = 100
    Ghost_Fighting = 100

    Fighting_Dragon = 101
    Dragon_Fighting = 101

    Fighting_Dark = 102
    Dark_Fighting = 102

    Fighting_Steel = 103
    Steel_Fighting = 103

    Fighting_Fairy = 104
    Fairy_Fighting = 104

    Poison = 105
    Poison_Poison = 105

    Poison_Ground = 106
    Ground_Poison = 106

    Poison_Flying = 107
    Flying_Poison = 107

    Poison_Psychic = 108
    Psychic_Poison = 108

    Poison_Bug = 109
    Bug_Poison = 109

    Poison_Rock = 110
    Rock_Poison = 110

    Poison_Ghost = 111
    Ghost_Poison = 111

    Poison_Dragon = 112
    Dragon_Poison = 112

    Poison_Dark = 113
    Dark_Poison = 113

    Poison_Steel = 114
    Steel_Poison = 114

    Poison_Fairy = 115
    Fairy_Poison = 115

    Ground = 116
    Ground_Ground = 116

    Ground_Flying = 117
    Flying_Ground = 117

    Ground_Psychic = 118
    Psychic_Ground = 118

    Ground_Bug = 119
    Bug_Ground = 119

    Ground_Rock = 120
    Rock_Ground = 120

    Ground_Ghost = 121
    Ghost_Ground = 121

    Ground_Dragon = 122
    Dragon_Ground = 122

    Ground_Dark = 123
    Dark_Ground = 123

    Ground_Steel = 124
    Steel_Ground = 124

    Ground_Fairy = 125
    Fairy_Ground = 125

    Flying = 126
    Flying_Flying = 126

    Flying_Psychic = 127
    Psychic_Flying = 127

    Flying_Bug = 128
    Bug_Flying = 128

    Flying_Rock = 129
    Rock_Flying = 129

    Flying_Ghost = 130
    Ghost_Flying = 130

    Flying_Dragon = 131
    Dragon_Flying = 131

    Flying_Dark = 132
    Dark_Flying = 132

    Flying_Steel = 133
    Steel_Flying = 133

    Flying_Fairy = 134
    Fairy_Flying = 134

    Psychic = 135
    Psychic_Psychic = 135

    Psychic_Bug = 136
    Bug_Psychic = 136

    Psychic_Rock = 137
    Rock_Psychic = 137

    Psychic_Ghost = 138
    Ghost_Psychic = 138

    Psychic_Dragon = 139
    Dragon_Psychic = 139

    Psychic_Dark = 140
    Dark_Psychic = 140

    Psychic_Steel = 141
    Steel_Psychic = 141

    Psychic_Fairy = 142
    Fairy_Psychic = 142

    Bug = 143
    Bug_Bug = 143

    Bug_Rock = 144
    Rock_Bug = 144

    Bug_Ghost = 145
    Ghost_Bug = 145

    Bug_Dragon = 146
    Dragon_Bug = 146

    Bug_Dark = 147
    Dark_Bug = 147

    Bug_Steel = 148
    Steel_Bug = 148

    Bug_Fairy = 149
    Fairy_Bug = 149

    Rock = 150
    Rock_Rock = 150

    Rock_Ghost = 151
    Ghost_Rock = 151

    Rock_Dragon = 152
    Dragon_Rock = 152

    Rock_Dark = 153
    Dark_Rock = 153

    Rock_Steel = 154
    Steel_Rock = 154

    Rock_Fairy = 155
    Fairy_Rock = 155

    Ghost = 156
    Ghost_Ghost = 156

    Ghost_Dragon = 157
    Dragon_Ghost = 157

    Ghost_Dark = 158
    Dark_Ghost = 158

    Ghost_Steel = 159
    Steel_Ghost = 159

    Ghost_Fairy = 160
    Fairy_Ghost = 160

    Dragon = 161
    Dragon_Dragon = 161

    Dragon_Dark = 162
    Dark_Dragon = 162

    Dragon_Steel = 163
    Steel_Dragon = 163

    Dragon_Fairy = 164
    Fairy_Dragon = 164

    Dark = 165
    Dark_Dark = 165

    Dark_Steel = 166
    Steel_Dark = 166

    Dark_Fairy = 167
    Fairy_Dark = 167

    Steel = 168
    Steel_Steel = 168

    Steel_Fairy = 169
    Fairy_Steel = 169

    Fairy = 170
    Fairy_Fairy = 170

    def display(self) -> list[TYPE]:
        """Get the display names of the types."""
        return cast(list[TYPE], self.name.split("_"))


SCORES = [
    0.06099708268989983,
    0.07609668309797292,
    0.07755098162773733,
    0.07528787581726906,
    0.06697917958709365,
    0.07042041698182097,
    0.06875172446240499,
    0.0694707402033407,
    0.07871372802753264,
    0.07323443566449268,
    0.0734142231474166,
    0.06896843606909984,
    0.07081173266313882,
    0.08114435019846389,
    0.06949257906575437,
    0.07174329343762528,
    0.08051413755887118,
    0.07707333217963225,
    0.07196733599403997,
    0.0822145977462367,
    0.08048466345048298,
    0.08008416541007814,
    0.07670186749098513,
    0.08061798471687527,
    0.07624386645555797,
    0.08776581339080189,
    0.08024170636459432,
    0.07842869458115684,
    0.07642054379060188,
    0.07792274132754143,
    0.08149382555217943,
    0.08108635221014555,
    0.07972598994678298,
    0.08132764024997748,
    0.08290273705547217,
    0.0738765670814289,
    0.08110635890290156,
    0.07508760465680409,
    0.07865085111906754,
    0.07859748991628117,
    0.08329739091634021,
    0.08586540296305616,
    0.08410507231498227,
    0.07687230328350217,
    0.0801906595523224,
    0.07886822172722424,
    0.08264157449142727,
    0.0814419756756884,
    0.07794116333602953,
    0.0849322782015798,
    0.08497007083544503,
    0.06678378352588568,
    0.07200421919651631,
    0.07786109803338916,
    0.07985640838887952,
    0.07850646723260973,
    0.08157617127878836,
    0.08188212837484066,
    0.07501370307342767,
    0.07833342663429348,
    0.07490521478869988,
    0.08075201112892263,
    0.07545277752902801,
    0.07617804292105185,
    0.08276417416423272,
    0.08279844458345843,
    0.058479650323857144,
    0.06882502896388686,
    0.06990635907412243,
    0.0720162836569761,
    0.0751690925656788,
    0.07250924800380361,
    0.06729986899770189,
    0.06367756447029613,
    0.07887237159370081,
    0.07510174996932503,
    0.06778473297611413,
    0.06840617970572468,
    0.08060977514310849,
    0.07258065142641656,
    0.06742960171786011,
    0.07712075551199601,
    0.07309356241777559,
    0.08328799877661246,
    0.07467707845151807,
    0.07190280073272544,
    0.06998267673901543,
    0.0729180612295194,
    0.07779417834499505,
    0.07363459971828158,
    0.07156548921918267,
    0.07870948133566741,
    0.07463488832787037,
    0.06321328111252883,
    0.07674894157543237,
    0.07688275392825408,
    0.07996061595312456,
    0.0798324598502394,
    0.07149471645065407,
    0.07753706634621016,
    0.08252510264731804,
    0.07615511893099207,
    0.0799705242159704,
    0.08384228267601063,
    0.07746595217275272,
    0.060234744856404975,
    0.08264010941333622,
    0.07383745923351437,
    0.07404715678160786,
    0.06839276056828127,
    0.07450480629943806,
    0.0774863885360134,
    0.0749698346445271,
    0.08246788120157773,
    0.08028592588010074,
    0.0766080953530492,
    0.07045358537239108,
    0.08810992765207135,
    0.0769272423378444,
    0.0805176476562979,
    0.07805291628650511,
    0.08218445669214106,
    0.08055778315435881,
    0.07872338504481863,
    0.08777148225173652,
    0.08603398554434964,
    0.07084952962955093,
    0.07216009079421647,
    0.07043408885235967,
    0.07825149419582203,
    0.07807127149925701,
    0.07453908951312235,
    0.0785742841357946,
    0.0877414002549554,
    0.07599463821579963,
    0.06406699776010721,
    0.0709343621377375,
    0.07312945035075082,
    0.07548329195052206,
    0.07054281590450659,
    0.07562311940066314,
    0.0800874072809677,
    0.07677641573068052,
    0.060195549536478946,
    0.07804257315381534,
    0.07538857286678381,
    0.06987853232264757,
    0.0703298589130096,
    0.08238821557889091,
    0.07149056170545819,
    0.06907626168614014,
    0.07761792265398405,
    0.07472088730144642,
    0.07261858900072435,
    0.07997836046033566,
    0.07979248624314776,
    0.06877145970112279,
    0.07811837052886945,
    0.07902191370033665,
    0.08683098360112304,
    0.08386573523321612,
    0.06552424292032369,
    0.07245435691951418,
    0.08577940828226004,
    0.07801175394504743,
    0.06833136120136728,
    0.08403167536389736,
    0.08080831490852695,
    0.07289999294553741,
    0.08771094821357792,
    0.07311026857313073,
]

Scores = {
    frozenset(("Normal",)): 0.06099708268989983,
    frozenset(("Normal", "Fire")): 0.07609668309797292,
    frozenset(("Normal", "Water")): 0.07755098162773733,
    frozenset(("Normal", "Electric")): 0.07528787581726906,
    frozenset(("Normal", "Grass")): 0.06697917958709365,
    frozenset(("Normal", "Ice")): 0.07042041698182097,
    frozenset(("Normal", "Fighting")): 0.06875172446240499,
    frozenset(("Normal", "Poison")): 0.0694707402033407,
    frozenset(("Normal", "Ground")): 0.07871372802753264,
    frozenset(("Normal", "Flying")): 0.07323443566449268,
    frozenset(("Normal", "Psychic")): 0.0734142231474166,
    frozenset(("Normal", "Bug")): 0.06896843606909984,
    frozenset(("Normal", "Rock")): 0.07081173266313882,
    frozenset(("Normal", "Ghost")): 0.08114435019846389,
    frozenset(("Normal", "Dragon")): 0.06949257906575437,
    frozenset(("Normal", "Dark")): 0.07174329343762528,
    frozenset(("Normal", "Steel")): 0.08051413755887118,
    frozenset(("Normal", "Fairy")): 0.07707333217963225,
    frozenset(("Fire",)): 0.07196733599403997,
    frozenset(("Fire", "Water")): 0.0822145977462367,
    frozenset(("Fire", "Electric")): 0.08048466345048298,
    frozenset(("Fire", "Grass")): 0.08008416541007814,
    frozenset(("Fire", "Ice")): 0.07670186749098513,
    frozenset(("Fire", "Fighting")): 0.08061798471687527,
    frozenset(("Fire", "Poison")): 0.07624386645555797,
    frozenset(("Fire", "Ground")): 0.08776581339080189,
    frozenset(("Fire", "Flying")): 0.08024170636459432,
    frozenset(("Fire", "Psychic")): 0.07842869458115684,
    frozenset(("Fire", "Bug")): 0.07642054379060188,
    frozenset(("Fire", "Rock")): 0.07792274132754143,
    frozenset(("Fire", "Ghost")): 0.08149382555217943,
    frozenset(("Fire", "Dragon")): 0.08108635221014555,
    frozenset(("Fire", "Dark")): 0.07972598994678298,
    frozenset(("Fire", "Steel")): 0.08132764024997748,
    frozenset(("Fire", "Fairy")): 0.08290273705547217,
    frozenset(("Water",)): 0.0738765670814289,
    frozenset(("Water", "Electric")): 0.08110635890290156,
    frozenset(("Water", "Grass")): 0.07508760465680409,
    frozenset(("Water", "Ice")): 0.07865085111906754,
    frozenset(("Water", "Fighting")): 0.07859748991628117,
    frozenset(("Water", "Poison")): 0.08329739091634021,
    frozenset(("Water", "Ground")): 0.08586540296305616,
    frozenset(("Water", "Flying")): 0.08410507231498227,
    frozenset(("Water", "Psychic")): 0.07687230328350217,
    frozenset(("Water", "Bug")): 0.0801906595523224,
    frozenset(("Water", "Rock")): 0.07886822172722424,
    frozenset(("Water", "Ghost")): 0.08264157449142727,
    frozenset(("Water", "Dragon")): 0.0814419756756884,
    frozenset(("Water", "Dark")): 0.07794116333602953,
    frozenset(("Water", "Steel")): 0.0849322782015798,
    frozenset(("Water", "Fairy")): 0.08497007083544503,
    frozenset(("Electric",)): 0.06678378352588568,
    frozenset(("Electric", "Grass")): 0.07200421919651631,
    frozenset(("Electric", "Ice")): 0.07786109803338916,
    frozenset(("Electric", "Fighting")): 0.07985640838887952,
    frozenset(("Electric", "Poison")): 0.07850646723260973,
    frozenset(("Electric", "Ground")): 0.08157617127878836,
    frozenset(("Electric", "Flying")): 0.08188212837484066,
    frozenset(("Electric", "Psychic")): 0.07501370307342767,
    frozenset(("Electric", "Bug")): 0.07833342663429348,
    frozenset(("Electric", "Rock")): 0.07490521478869988,
    frozenset(("Electric", "Ghost")): 0.08075201112892263,
    frozenset(("Electric", "Dragon")): 0.07545277752902801,
    frozenset(("Electric", "Dark")): 0.07617804292105185,
    frozenset(("Electric", "Steel")): 0.08276417416423272,
    frozenset(("Electric", "Fairy")): 0.08279844458345843,
    frozenset(("Grass",)): 0.058479650323857144,
    frozenset(("Grass", "Ice")): 0.06882502896388686,
    frozenset(("Grass", "Fighting")): 0.06990635907412243,
    frozenset(("Grass", "Poison")): 0.0720162836569761,
    frozenset(("Grass", "Ground")): 0.0751690925656788,
    frozenset(("Grass", "Flying")): 0.07250924800380361,
    frozenset(("Grass", "Psychic")): 0.06729986899770189,
    frozenset(("Grass", "Bug")): 0.06367756447029613,
    frozenset(("Grass", "Rock")): 0.07887237159370081,
    frozenset(("Grass", "Ghost")): 0.07510174996932503,
    frozenset(("Grass", "Dragon")): 0.06778473297611413,
    frozenset(("Grass", "Dark")): 0.06840617970572468,
    frozenset(("Grass", "Steel")): 0.08060977514310849,
    frozenset(("Grass", "Fairy")): 0.07258065142641656,
    frozenset(("Ice",)): 0.06742960171786011,
    frozenset(("Ice", "Fighting")): 0.07712075551199601,
    frozenset(("Ice", "Poison")): 0.07309356241777559,
    frozenset(("Ice", "Ground")): 0.08328799877661246,
    frozenset(("Ice", "Flying")): 0.07467707845151807,
    frozenset(("Ice", "Psychic")): 0.07190280073272544,
    frozenset(("Ice", "Bug")): 0.06998267673901543,
    frozenset(("Ice", "Rock")): 0.0729180612295194,
    frozenset(("Ice", "Ghost")): 0.07779417834499505,
    frozenset(("Ice", "Dragon")): 0.07363459971828158,
    frozenset(("Ice", "Dark")): 0.07156548921918267,
    frozenset(("Ice", "Steel")): 0.07870948133566741,
    frozenset(("Ice", "Fairy")): 0.07463488832787037,
    frozenset(("Fighting",)): 0.06321328111252883,
    frozenset(("Fighting", "Poison")): 0.07674894157543237,
    frozenset(("Fighting", "Ground")): 0.07688275392825408,
    frozenset(("Fighting", "Flying")): 0.07996061595312456,
    frozenset(("Fighting", "Psychic")): 0.0798324598502394,
    frozenset(("Fighting", "Bug")): 0.07149471645065407,
    frozenset(("Fighting", "Rock")): 0.07753706634621016,
    frozenset(("Fighting", "Ghost")): 0.08252510264731804,
    frozenset(("Fighting", "Dragon")): 0.07615511893099207,
    frozenset(("Fighting", "Dark")): 0.0799705242159704,
    frozenset(("Fighting", "Steel")): 0.08384228267601063,
    frozenset(("Fighting", "Fairy")): 0.07746595217275272,
    frozenset(("Poison",)): 0.060234744856404975,
    frozenset(("Poison", "Ground")): 0.08264010941333622,
    frozenset(("Poison", "Flying")): 0.07383745923351437,
    frozenset(("Poison", "Psychic")): 0.07404715678160786,
    frozenset(("Poison", "Bug")): 0.06839276056828127,
    frozenset(("Poison", "Rock")): 0.07450480629943806,
    frozenset(("Poison", "Ghost")): 0.0774863885360134,
    frozenset(("Poison", "Dragon")): 0.0749698346445271,
    frozenset(("Poison", "Dark")): 0.08246788120157773,
    frozenset(("Poison", "Steel")): 0.08028592588010074,
    frozenset(("Poison", "Fairy")): 0.0766080953530492,
    frozenset(("Ground",)): 0.07045358537239108,
    frozenset(("Ground", "Flying")): 0.08810992765207135,
    frozenset(("Ground", "Psychic")): 0.0769272423378444,
    frozenset(("Ground", "Bug")): 0.0805176476562979,
    frozenset(("Ground", "Rock")): 0.07805291628650511,
    frozenset(("Ground", "Ghost")): 0.08218445669214106,
    frozenset(("Ground", "Dragon")): 0.08055778315435881,
    frozenset(("Ground", "Dark")): 0.07872338504481863,
    frozenset(("Ground", "Steel")): 0.08777148225173652,
    frozenset(("Ground", "Fairy")): 0.08603398554434964,
    frozenset(("Flying",)): 0.07084952962955093,
    frozenset(("Flying", "Psychic")): 0.07216009079421647,
    frozenset(("Flying", "Bug")): 0.07043408885235967,
    frozenset(("Flying", "Rock")): 0.07825149419582203,
    frozenset(("Flying", "Ghost")): 0.07807127149925701,
    frozenset(("Flying", "Dragon")): 0.07453908951312235,
    frozenset(("Flying", "Dark")): 0.0785742841357946,
    frozenset(("Flying", "Steel")): 0.0877414002549554,
    frozenset(("Flying", "Fairy")): 0.07599463821579963,
    frozenset(("Psychic",)): 0.06406699776010721,
    frozenset(("Psychic", "Bug")): 0.0709343621377375,
    frozenset(("Psychic", "Rock")): 0.07312945035075082,
    frozenset(("Psychic", "Ghost")): 0.07548329195052206,
    frozenset(("Psychic", "Dragon")): 0.07054281590450659,
    frozenset(("Psychic", "Dark")): 0.07562311940066314,
    frozenset(("Psychic", "Steel")): 0.0800874072809677,
    frozenset(("Psychic", "Fairy")): 0.07677641573068052,
    frozenset(("Bug",)): 0.060195549536478946,
    frozenset(("Bug", "Rock")): 0.07804257315381534,
    frozenset(("Bug", "Ghost")): 0.07538857286678381,
    frozenset(("Bug", "Dragon")): 0.06987853232264757,
    frozenset(("Bug", "Dark")): 0.0703298589130096,
    frozenset(("Bug", "Steel")): 0.08238821557889091,
    frozenset(("Bug", "Fairy")): 0.07149056170545819,
    frozenset(("Rock",)): 0.06907626168614014,
    frozenset(("Rock", "Ghost")): 0.07761792265398405,
    frozenset(("Rock", "Dragon")): 0.07472088730144642,
    frozenset(("Rock", "Dark")): 0.07261858900072435,
    frozenset(("Rock", "Steel")): 0.07997836046033566,
    frozenset(("Rock", "Fairy")): 0.07979248624314776,
    frozenset(("Ghost",)): 0.06877145970112279,
    frozenset(("Ghost", "Dragon")): 0.07811837052886945,
    frozenset(("Ghost", "Dark")): 0.07902191370033665,
    frozenset(("Ghost", "Steel")): 0.08683098360112304,
    frozenset(("Ghost", "Fairy")): 0.08386573523321612,
    frozenset(("Dragon",)): 0.06552424292032369,
    frozenset(("Dragon", "Dark")): 0.07245435691951418,
    frozenset(("Dragon", "Steel")): 0.08577940828226004,
    frozenset(("Dragon", "Fairy")): 0.07801175394504743,
    frozenset(("Dark",)): 0.06833136120136728,
    frozenset(("Dark", "Steel")): 0.08403167536389736,
    frozenset(("Dark", "Fairy")): 0.08080831490852695,
    frozenset(("Steel",)): 0.07289999294553741,
    frozenset(("Steel", "Fairy")): 0.08771094821357792,
    frozenset(("Fairy",)): 0.07311026857313073,
}
