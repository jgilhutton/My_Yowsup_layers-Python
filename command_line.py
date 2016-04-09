# -*- coding: utf-8 -*-
import subprocess
from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
import threading
import logging
logger = logging.getLogger(__name__)

class QueryLayer(YowInterfaceLayer):
  
    def __init__(self):
        super(QueryLayer, self).__init__()
        self.ackQueue = []
        self.lock = threading.Condition()

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):
        self.lock.acquire()
	self.toLower(messageProtocolEntity.ack())  # ACKS
	self.toLower(messageProtocolEntity.ack(True))
        numeros = ['Your number']
	msg = messageProtocolEntity.getBody()  # MENSAJE
        if messageProtocolEntity.getType() == 'text' and numeros[0] in messageProtocolEntity.getFrom():
	    query = self.onTextMessage(messageProtocolEntity)
	    if query == 'Ok':
	      self.Respuesta('Ok',messageProtocolEntity.getFrom())
	    elif query:
	      self.Respuesta(query,messageProtocolEntity.getFrom())
	    else:
	      self.Respuesta('Error',messageProtocolEntity.getFrom())
	else:
	  print messageProtocolEntity.getFrom()+':  '+msg+'\n'
	self.lock.release()

    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        self.lock.acquire()
        self.toLower(entity.ack())
	self.lock.release()

    def onAck(self, entity):
        self.lock.acquire()
        if entity.getId() in self.ackQueue:
            self.ackQueue.pop(self.ackQueue.index(entity.getId()))
            
        if not len(self.ackQueue):
            self.lock.release()
            print "Comando enviado\n"
        self.lock.release()
        
    def Respuesta(self, query, numero):

        self.lock.acquire()

	messageEntity = TextMessageProtocolEntity(query, to = numero)
	self.ackQueue.append(messageEntity.getId())
	self.toLower(messageEntity)
	self.onAck(messageEntity)

        self.lock.release()

    def onTextMessage(self,messageProtocolEntity):
        self.lock.acquire()
	cmd = messageProtocolEntity.getBody()
        print "CMD: %s" %cmd
	cmd = cmd.strip().lstrip()
	output = ''
	try:
	  output = subprocess.check_output(cmd, shell = True)
	  if output == '':return 'Ok'
	except: return ''
	print output.strip()
	return output
        self.lock.release()
