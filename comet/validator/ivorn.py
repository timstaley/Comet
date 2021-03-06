# Comet VOEvent Broker.
# Check for valid IVORN.

from zope.interface import implementer
from comet.icomet import IValidator
from comet.utility import parse_ivorn

__all__ = ["CheckIVORN"]

@implementer(IValidator)
class CheckIVORN(object):
    """
    Check that the event received has an IVORN that corresponds to the
    description in "IVOA Identifiers Version 1.12" by Plante et al *and*
    provides a "local_ID" as per the VOEvent 2.0 spec (basically a fragment
    following a #).
    """
    def __call__(self, event):
        # parse_ivorn() raises if whatever it's being parsed
        auth, rsrc, local_ID = parse_ivorn(event.attrib['ivorn'])
        if not local_ID:
            raise Exception("No per-event local ID")
