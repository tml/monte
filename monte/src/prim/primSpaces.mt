module OrderedSpaceMaker
export (charSpace, intSpace, floatSpace, __makeOrderedSpace)

def charSpace := OrderedSpaceMaker(char, "char")
def intSpace := OrderedSpaceMaker(int, "int")
def floatSpace := OrderedSpaceMaker(float, "float")

object __makeOrderedSpace extends OrderedSpaceMaker:
    /**
     * Given a value of a type whose reflexive (x <=> x) instances are
     * fully ordered, this returns the corresponding OrderedSpace
     */
    to spaceOfValue(value):
        if (value =~ i :int):
            return intSpace
        else if (value =~ f :float):
            return floatSpace
        else if (value =~ c :char):
            return charSpace
        else:
            def type := value._getAllegedType()
            return OrderedSpaceMaker(type, M.toQuote(type))

    /**
     * start..!bound is equivalent to
     * (space >= start) & (space < bound)
     */
    to op__till(start, bound):
        def space := __makeOrderedSpace.spaceOfValue(start)
        return (space >= start) & (space < bound)

    /**
     * start..stop is equivalent to
     * (space >= start) & (space <= stop)
     */
    to op__thru(start, stop):
        def space := __makeOrderedSpace.spaceOfValue(start)
        return (space >= start) & (space <= stop)
