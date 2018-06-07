gyroData = []
accelData = []
pressureData = []
altitudeData = []
orientationData = []
gpsData = []

class SyntaxParser():
    START_LINE = "@{"
    END_LINE = "}@"
    TIMING = ";"
    GYRO_SYNTAX = ["GX:", "GY:", "GZ:", "TS:"]
    ACCEL_SYNTAX = ["AX:", "AY:", "AZ:", "TS:"]
    ORIENTATION_SYNTAX = ["OX:", "OY:", "OZ:", "TS:"]
    PRESSURE_SYNTAX = ["PS:", "TS:"]
    ALTITUDE_SYNTAX = ["PA:", "TS:"]

    def parseLine(self, line):
        syntax = self.getSyntax(line)
        data = []
        startIndex = line.index(self.START_LINE)
        endIndex = line.index(self.END_LINE)
        for i in range(0, len(syntax)):
            if(i < len(syntax)-1):
                data.append(line[line.index(syntax[i])+3:line.index(syntax[i+1])-1])
            else:
                data.append(line[line.index(syntax[i])+3:endIndex-1])
        return data

    def getSyntax(self, line):
        startIndex = line.index(self.START_LINE)
        testSyntax = line[startIndex+2:startIndex+5]
        if(testSyntax == self.GYRO_SYNTAX[0]):
            return self.GYRO_SYNTAX
        elif(testSyntax == self.ACCEL_SYNTAX[0]):
            return self.ACCEL_SYNTAX
        elif(testSyntax == self.ORIENTATION_SYNTAX[0]):
            return self.ORIENTATION_SYNTAX
        elif(testSyntax == self.PRESSURE_SYNTAX[0]):
            return self.PRESSURE_SYNTAX
        elif(testSyntax == self.ALTITUDE_SYNTAX[0]):
            return self.ALTITUDE_SYNTAX

def main():
    parser = SyntaxParser()
    f = open("./FDAT1.TXT", "r")
    for sampleLine in f:
        sampleData = parser.parseLine(sampleLine)
        print(sampleData)

if __name__ == "__main__":
    main()
