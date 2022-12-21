class Level:  
    def __init__(self, number, startText, endText, operations, numbers, goal, type, twoD):
        self.number = number
        self.startText = startText
        self.endText = endText
        self.operations = operations
        self.numbers = numbers
        self.goal = goal
        self.type = type
        self.twoD = twoD

    def __str__(self):
        output = "Level {0}:\n{1}\nValid Operations: ".format(self.number, self.startText)
        for i in range(0, len(self.operations)):
            output += self.operations[i] + " "
        output += "\nGiven Numbers: "
        for i in range(0, len(self.numbers)):
            output += self.numbers[i] + " "
        output += "\nGoal: ({0}, {1})".format(self.goal["x"], self.goal["y"])
        output += "\n" + self.endText
        output += "\Type: " + self.type
        return output

    def from_json(json_dct):
        return Level(json_dct['number'], json_dct['start_text'], json_dct['end_text'],
                     json_dct['operations'], json_dct['numbers'],
                     json_dct['goal'], json_dct['type'], json_dct['two_d'])