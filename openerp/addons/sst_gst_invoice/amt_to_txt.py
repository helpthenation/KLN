class Number2Words(object):

        def __init__(self):
            '''Initialise the class with useful data'''

            self.wordsDict = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven',
                              8: 'Eight', 9: 'Nine', 10: 'Ten', 11: 'Eleven', 12: 'Twelve', 13: 'Thirteen',
                              14: 'Fourteen', 15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen',
                              18: 'Eighteen', 19: 'Nineteen', 20: 'Twenty', 30: 'Thirty', 40: 'Forty',
                              50: 'Fifty', 60: 'Sixty', 70: 'Seventy', 80: 'Eighty', 90: 'Ninety' }

            self.powerNameList = ['Thousand', 'Lakhs', 'Crores']


        def convertNumberToWords(self, number):

            # Check if there is decimal in the number. If Yes process them as paisa part.
            formString = str(number)
            if formString.find('.') != -1:
                withoutDecimal, decimalPart = formString.split('.')

                paisaPart =  str(round(float(formString), 2)).split('.')[1]
                inPaisa = self._formulateDoubleDigitWords(paisaPart)

                formString, formNumber = str(withoutDecimal), int(withoutDecimal)
            else:
                # Process the number part without decimal separately
                formNumber = int(number)
                inPaisa = None

            if not formNumber:
                return 'zero'

            self._validateNumber(formString, formNumber)

            inRupees = self._convertNumberToWords(formString)

            if inPaisa:
                return '%s Rupees And %s Paisa Only' % (inRupees.title(), inPaisa.title())
            else:
                return ' %s  Rupees Only'  % inRupees.title()


        def _validateNumber(self, formString, formNumber):

            assert formString.isdigit()

            # Developed to provide words upto 999999999
            if formNumber > 999999999 or formNumber < 0:
                raise AssertionError('Out Of range')


        def _convertNumberToWords(self, formString):

            MSBs, hundredthPlace, teens = self._getGroupOfNumbers(formString)

            wordsList = self._convertGroupsToWords(MSBs, hundredthPlace, teens)

            return ' '.join(wordsList)


        def _getGroupOfNumbers(self, formString):

            hundredthPlace, teens = formString[-3:-2], formString[-2:]

            msbUnformattedList = list(formString[:-3])

            #---------------------------------------------------------------------#

            MSBs = []
            tempstr = ''
            for num in msbUnformattedList[::-1]:
                tempstr = '%s%s' % (num, tempstr)
                if len(tempstr) == 2:
                    MSBs.insert(0, tempstr)
                    tempstr = ''
            if tempstr:
                MSBs.insert(0, tempstr)

            #---------------------------------------------------------------------#

            return MSBs, hundredthPlace, teens


        def _convertGroupsToWords(self, MSBs, hundredthPlace, teens):

            wordList = []

            #---------------------------------------------------------------------#
            if teens:
                teens = int(teens)
                tensUnitsInWords = self._formulateDoubleDigitWords(teens)
                if tensUnitsInWords:
                    wordList.insert(0, tensUnitsInWords)

            #---------------------------------------------------------------------#
            if hundredthPlace:
                hundredthPlace = int(hundredthPlace)
                if not hundredthPlace:
                    # Might be zero. Ignore.
                    pass
                else:
                    hundredsInWords = '%s hundred and' % self.wordsDict[hundredthPlace]
                    wordList.insert(0, hundredsInWords)

            #---------------------------------------------------------------------#
            if MSBs:
                MSBs.reverse()

                for idx, item in enumerate(MSBs):
                    inWords = self._formulateDoubleDigitWords(item)
                    if inWords:
                        inWordsWithDenomination = '%s %s' % (inWords, self.powerNameList[idx])
                        wordList.insert(0, inWordsWithDenomination)

            #---------------------------------------------------------------------#
            return wordList


        def _formulateDoubleDigitWords(self, doubleDigit):

            if not int(doubleDigit):
                # Might be zero. Ignore.
                return None
            elif self.wordsDict.has_key(int(doubleDigit)):
                # Global dict has the key for this number
                tensInWords = self.wordsDict[int(doubleDigit)]
                return tensInWords
            else:
                doubleDigitStr = str(doubleDigit)
                tens, units = int(doubleDigitStr[0])*10, int(doubleDigitStr[1])
                tensUnitsInWords = '%s %s' % (self.wordsDict[tens], self.wordsDict[units])
                return tensUnitsInWords


#~ if __name__ == '__main__':
#~ 
    #~ wGenerator = Number2Words()
    #~ print wGenerator.convertNumberToWords(2374356)
