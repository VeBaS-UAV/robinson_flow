import json
from PyFlow.Core import PinBase

from pymavlink.dialects.v20.ardupilotmega import MAVLink_message

class MAVlink_pyflow_dummy(MAVLink_message):
    def __init__(self, msgId=-1, name='pyflow_dummy'):
        super().__init__(msgId, name)

class MavlinkJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MAVLink_message):
            data = obj.to_dict()
            del data["mavpackettype"]

            json_msg = data.copy()
            json_msg["mavpackettype"] = obj.get_type()

            return json_msg
        return json.JSONEncoder.default(self, obj)

class MavlinkPin(PinBase):
    """doc string for MavlinkPin"""
    def __init__(self, name, parent, direction, **kwargs):
        super(MavlinkPin, self).__init__(name, parent, direction, **kwargs)
        self.logger = getLogger(name)

        self.setDefaultValue(False)

    @staticmethod
    def IsValuePin():
        return True

    @staticmethod
    def supportedDataTypes():
        return ('MavlinkPin',)

    @staticmethod
    def pinDataTypeHint():
        return 'MavlinkPin', False

    @staticmethod
    def color():
        return (80, 190, 50, 255)

    @staticmethod
    def internalDataStructure():
        return MAVlink_pyflow_dummy

    @staticmethod
    def processData(data):
        if isinstance(data, MAVLink_message):
            return data
        return MavlinkPin.internalDataStructure()(data)

    @staticmethod
    def jsonEncoderClass():
        """Returns json encoder class for this pin
        """
        return MavlinkJsonEncoder
