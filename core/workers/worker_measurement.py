#!/usr/bin python
import core.utils.logging as log
from core.messages import MessageSplit, MessageMeasurement
import json


class WorkerMeasurement:
    def __init__(self, session_detail_id=0, worker_name='', device_name='',
                 value=0.0, set_point=0.0, work='', remaining='', debug_timer=None):
        self.session_detail_id = session_detail_id
        self.worker_name = worker_name
        self.device_name = device_name
        self.value = value
        self.set_point = set_point
        self.work = work
        self.remaining = remaining
        if debug_timer is None:
            self.debug_timer = None
        else:
            self.debug_timer = str(debug_timer)


    @staticmethod
    def serialize_message(worker_measurement):
        if worker_measurement is None:
            log.error('Unable to deserialize worker measurement, object is None')
        if not worker_measurement.__class__ is WorkerMeasurement:
            log.error('Unable to serialize worker measurement, object is of type {0}'.
                      format(worker_measurement.__class__.__name))
        else:
            try:
                if not worker_measurement.debug_timer is None:
                    worker_measurement.debug_timer = str(worker_measurement.debug_timer)
                return MessageMeasurement + MessageSplit + json.dumps(worker_measurement.__dict__)
            except Exception:
                log.error('Unable to serialize worker measurement, object is {0}'.
                          format(worker_measurement))
        return None

    @staticmethod
    def deserialize_message(serialized_worker_measurement):
        if serialized_worker_measurement is None:
            log.error('Unable to deserialize worker measurement, serialized object is None')
        if not serialized_worker_measurement.startswith(MessageMeasurement + MessageSplit):
            log.error('Serialized worker measurement should begin with {0}{1}'.format(MessageMeasurement, MessageSplit))
        else:
            try:
                serialized_worker_measurement = serialized_worker_measurement[len(MessageMeasurement+MessageSplit):]
                worker_measurement_data = json.loads(serialized_worker_measurement)
                worker_measurement = WorkerMeasurement()
                worker_measurement.session_detail_id = worker_measurement_data['session_detail_id']
                worker_measurement.worker_name = worker_measurement_data['worker_name']
                worker_measurement.device_name = worker_measurement_data['device_name']
                worker_measurement.value = worker_measurement_data['value']
                worker_measurement.set_point = worker_measurement_data['set_point']
                worker_measurement.work = worker_measurement_data['work']
                worker_measurement.remaining = worker_measurement_data['remaining']
                if 'debug_timer' in worker_measurement_data.keys():
                    worker_measurement.debug_timer = worker_measurement_data['debug_timer']
                else:
                    worker_measurement.debug_timer = None

                return worker_measurement
            except Exception:
                log.error('Unable to deserialize worker measurement, serialized object is {0}'.
                          format(serialized_worker_measurement))
        return None