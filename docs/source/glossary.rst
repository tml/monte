========
Glossary
========

.. glossary::

    message
        An object of the form ``[verb :Str, args :List, namedArgs :Map]``
        which is passed from calling objects to target objects to faciliate
        computation.

    verb
        A string which forms the first element of a message.

    ejector : Coercion
        An object which can be called once to prematurely end control flow.

    guard : Coercion
        An object which provides the coercion protocol.

    prize : Coercion
        The result of a successful coercion.
