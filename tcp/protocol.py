# VOEvent TCP transport protocol using Twisted.
# John Swinbank, <swinbank@transientskp.org>, 2011-12.

# XML parsing using ElementTree
import xml.etree.ElementTree as ElementTree

# Twisted protocol definition
from twisted.python import log
from twisted.protocols.basic import Int32StringReceiver
from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Factory
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ReconnectingClientFactory

# Constructors for transport protocol messages
from .messages import Ack, IAmAlive, IAmAliveResponse

# Constants
VOEVENT_ROLES = ('observation', 'prediction', 'utility', 'test')

"""
Implements the VOEvent Transport Protocol; see
<http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

All messages consist of a 4-byte network ordered payload size followed by the
payload data. Twisted's Int32StringReceiver handles this for us automatically.

There are four different VOEvent protocols to implement:

* VOEventSubscriber

    * Opens connection to remote broker, receives VOEvent messages.

* VOEventPublisher

    * Listens for connections from subscribers, sends VOEvent messages.

* VOEventSender

    * Connects to VOEventReceiver and publishes a new message.

* VOEventReceiver

    * Receives messages from VOEventSender.

To implement the broker, we need the Subscriber, Publisher & Receiver, but not
the Sender. All four are implemented here for completeness.
"""

class VOEventSubscriber(Int32StringReceiver):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages consist of a 4-byte network ordered payload size followed by
    the payload data. Twisted's Int32StringReceiver handles this for us
    automatically.

    When a VOEvent is received, we broadcast it onto a ZeroMQ PUB socket.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.

        We have two jobs here:

        1. Reply according to the Transport Protocol.
        2. Call a local event handler, voEventHandler(), defined in subclass.
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        # Handle our transport protocol obligations.
        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') == "iamalive":
            log.msg("IAmAlive received")
            outgoing = IAmAliveResponse(self.factory.local_ivo, incoming.find('Origin').text)
        elif incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received")
            outgoing = Ack(self.factory.local_ivo, incoming.attrib['ivorn'])
            self.voEventHandler(incoming)
        else:
            log.err("Incomprehensible data received")
        try:
            self.sendString(outgoing.to_string())
            log.msg("Sent response")
        except NameError:
            log.msg("No response to send")

    def voEventHandler(self, event):
        """
        End-users should define voEventHandler which is called when an event
        is received.
        """
        log.msg("Event received")
##        raise NotImplementedError("Subclass VOEventSubscrber to define handlers")

class VOEventSubscriberFactory(ReconnectingClientFactory):
    protocol = VOEventSubscriber
    def __init__(self, local_ivo):
        self.local_ivo = local_ivo

    def buildProtocol(self, addr):
        self.resetDelay()
        p = self.protocol()
        p.factory = self
        return p


class VOEventPublisher(Int32StringReceiver):
    def connectionMade(self):
        self.factory.publishers.append(self)
        self.alive_count = 0

    def connectionLost(self, reason):
        self.factory.publishers.remove(self)

    def sendIAmAlive(self):
        if self.alive_count > 1:
            log.msg("Peer appears to be dead; dropping connection")
            self.transport.abortConnection()
        else:
            self.sendString(IAmAlive(self.factory.local_ivo).to_string())
            self.alive_count += 1
            log.msg("Sent iamalive %d" % self.alive_count)

    def sendEvent(self, event):
        self.sendString(ElementTree.tostring(event))
        log.msg("Sent event")

    def stringReceived(self, data):
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        if incoming.get('role') == "iamalive":
            log.msg("IAmAlive received")
            self.alive_count -= 1
        else:
            log.err("Incomprehensible data received")


class VOEventPublisherFactory(ServerFactory):
    protocol = VOEventPublisher
    def __init__(self, local_ivo):
        self.local_ivo = local_ivo
        self.publishers = []
        self.alive_loop = LoopingCall(self.sendIAmAlive)
        self.alive_loop.start(5)

    def sendIAmAlive(self):
        for publisher in self.publishers:
            publisher.sendIAmAlive()


class VOEventSender(Int32StringReceiver):
    """
    Implements the VOEvent Transport Protocol; see
    <http://www.ivoa.net/Documents/Notes/VOEventTransport/>.

    All messages consist of a 4-byte network ordered payload size followed by
    the payload data. Twisted's Int32StringReceiver handles this for us
    automatically.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        log.msg("Got response")
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")
            return

        if incoming.get('role') == "ack":
            log.msg("Acknowledgement received")
        else:
            log.err("Incomprehensible data received")

        # After receiving a message, we shut down the connection.
        self.transport.loseConnection()

class VOEventSenderFactory(Factory):
    protocol = VOEventSender


class VOEventReceiver(Int32StringReceiver):
    """
    When a VOEvent is received, we acknowledge it, shut down the connection,
    and call VOEventReceiver.voEventHandler() to process it. That method
    should be supplied in a subclass.
    """
    def stringReceived(self, data):
        """
        Called when a complete new message is received.
        """
        try:
            incoming = ElementTree.fromstring(data)
        except ElementTree.ParseError:
            log.err("Unparsable message received")

        # Handle our transport protocol obligations.
        # The root element of both VOEvent and Transport packets has a
        # "role" element which we use to identify the type of message we
        # have received.
        if incoming.get('role') in VOEVENT_ROLES:
            log.msg("VOEvent received")
            outgoing = Ack(self.factory.local_ivo, incoming.attrib['ivorn'])
        else:
            log.err("Incomprehensible data received")
        try:
            self.sendString(outgoing.to_string())
            log.msg("Sent response")
        except NameError:
            log.msg("No response to send")

        # After receiving an event, we shut down the connection.
        self.transport.loseConnection()

        # Call the local handler
        self.voEventHandler(incoming)

    def voEventHandler(self, event):
        """
        End-users should define voEventHandler which is called when an event
        is received.
        """
        raise NotImplementedError("Subclass VOEventReceiver to define handlers")

class VOEventReceiverFactory(ServerFactory):
    protocol = VOEventReceiver
    def __init__(self, local_ivo):
        self.local_ivo = local_ivo