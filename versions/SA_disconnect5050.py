import versions.SlottedAloha as SlottedAloha
import random

NORM_VOLTAGE = 230

meta = {
    'versions': {
        'AlohaOben': {
            'public': True,
            'any_inputs': True,
            'params': ['node_id', 'id', 'seed'],
            'attrs': ['node_id', 'voltage', 'Vm', 'Va', 'P_out', 'Q_out', 'arrival_time', 'departure_time',
                      'available', 'current_soc', 'possible_charge_rate', 'Q', 'P'],
        },
    }
}


class SlottedAloha_disconnect5050(SlottedAloha):

    def __init__(self, node_id, id, seed):
        self.step_size = 60
        self.node_id = node_id
        self.id = id
        self.seed = seed
        self.participants = 0
        self.chargingFLAG = False
        self.waitingTime = 0
        self.P_out = 0.0
        self.P_old = 0.0
        self.disconnectFLAG = False

    def step(self, simTime, inputs, participants):
        self.participants = participants
        if self.getAtt('available', inputs) & (self.getAtt('current_soc', inputs) < 100.0):
            if (not self.chargingFLAG) & (self.waitingTime == 0):  # not charging right now, but waiting time is over
                self.charging(inputs)
            elif (not self.chargingFLAG) & (self.waitingTime > 0):  # not charging right now, waiting time not yet over
                self.waitingTime -= 1
            elif self.chargingFLAG:  # charging right now, time is not over
                self.charging(inputs)
        else:
            self.chargingFLAG = False
            self.P_out = 0.0

    def charging(self, inputs):
        P = self.calcPower(inputs)

        if P > 0:
            self.P_out = P
            self.P_old = P
            self.chargingFLAG = True
        else:
            self.determineDisconnect()
            if self.disconnectFLAG:
                self.P_out = 0.0
                self.chargingFLAG = False
                self.waitingTime = self.calculateWaitingTime()
            else:
                self.P_out = self.P_old
                self.chargingFLAG = False

    def determineDisconnect(self):
        random.seed(self.seed)
        result = random.randrange(0, 2, 1)
        if result == 1:
            self.disconnectFLAG = True
        else:
            self.disconnectFLAG = False
