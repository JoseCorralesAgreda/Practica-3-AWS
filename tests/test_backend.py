"""Pruebas del contrato Alexa/AWS sin red ni credenciales reales."""
import copy
import io
import json
import time
import unittest
from unittest.mock import Mock

from botocore.exceptions import ClientError
from backend.lambda_function import AmbientadorSkill


def aws_error(code):
    return ClientError({"Error": {"Code": code, "Message": "simulado"}}, "Test")


class SkillTests(unittest.TestCase):
    def setUp(self):
        self.table, self.iot, self.shadow = Mock(), Mock(), Mock()
        self.skill = AmbientadorSkill(self.table, self.iot, self.shadow, "skill-test")
        self.table.get_item.return_value = {"Item": {"thingName": "thing"}}
        self.document = {"version": 7, "state": {"reported": {
            "sampledAt": int(time.time()), "presence": True, "pirReady": True,
            "automatic": False, "servoState": "idle", "activationId": "anterior",
        }, "desired": {"activationId": "anterior"}}}
        self.shadow.get_thing_shadow.side_effect = lambda **kwargs: {
            "payload": io.BytesIO(json.dumps(self.document).encode())}

    def event(self, name, user="usuario-uno", slots=None):
        return {"context": {"System": {"application": {"applicationId": "skill-test"},
                                         "user": {"userId": user}}},
                "request": {"type": "IntentRequest", "requestId": "peticion-001",
                            "intent": {"name": name, "slots": slots or {}}}}

    def speech(self, event):
        return self.skill.handle(event)["response"]["outputSpeech"]["text"]

    def test_unlinked_user_is_guided_without_iot_call(self):
        self.table.get_item.return_value = {}
        self.assertIn("vincula", self.speech(self.event("ActivarIntent")))
        self.shadow.update_thing_shadow.assert_not_called()

    def test_link_checks_existence_and_persists(self):
        self.speech(self.event("VincularIntent", slots={"thingName": {"value": "thing"}}))
        self.iot.describe_thing.assert_called_once_with(thingName="thing")
        item = self.table.put_item.call_args.kwargs["Item"]
        self.assertEqual(item["userId"], "usuario-uno")
        self.assertEqual(item["thingName"], "thing")
        self.assertIn("fechaVinculacion", item)

    def test_nonexistent_thing_does_not_replace_binding(self):
        self.iot.describe_thing.side_effect = aws_error("ResourceNotFoundException")
        self.assertIn("no existe", self.speech(self.event("VincularIntent", slots={"thingName": {"value": "missing"}})))
        self.table.put_item.assert_not_called()

    def test_invalid_name_is_rejected(self):
        self.speech(self.event("VincularIntent", slots={"thingName": {"value": "bad/name"}}))
        self.iot.describe_thing.assert_not_called()

    def test_slot_synonym_uses_canonical_name(self):
        slot = {"value": "ambientador dos", "resolutions": {"resolutionsPerAuthority": [{
            "status": {"code": "ER_SUCCESS_MATCH"}, "values": [{"value": {"name": "ambientador-dos"}}]}]}}
        self.speech(self.event("VincularIntent", slots={"thingName": slot}))
        self.iot.describe_thing.assert_called_with(thingName="ambientador-dos")

    def test_unlink_uses_current_user(self):
        self.speech(self.event("DesvincularIntent", user="usuario-dos"))
        self.table.delete_item.assert_called_once_with(Key={"userId": "usuario-dos"})

    def test_commands_resolve_each_user(self):
        self.table.get_item.side_effect = [{"Item": {"thingName": "thing"}}, {"Item": {"thingName": "ambientador-dos"}}]
        for user in ("usuario-uno", "usuario-dos"):
            self.speech(self.event("ActivarIntent", user=user))
        names = [call.kwargs["thingName"] for call in self.shadow.update_thing_shadow.call_args_list]
        self.assertEqual(names, ["thing", "ambientador-dos"])
        self.assertTrue(all(call.kwargs["ConsistentRead"] for call in self.table.get_item.call_args_list))

    def test_command_changes_only_desired_with_version(self):
        self.assertIn("Envié", self.speech(self.event("ActivarIntent")))
        payload = json.loads(self.shadow.update_thing_shadow.call_args.kwargs["payload"])
        self.assertEqual(payload, {"version": 7, "state": {"desired": {"activationId": "peticion-001"}}})

    def test_repeated_request_does_not_send_again(self):
        self.document["state"]["desired"]["activationId"] = "peticion-001"
        self.assertIn("ya fue enviada", self.speech(self.event("ActivarIntent")))
        self.shadow.update_thing_shadow.assert_not_called()

    def test_pending_command_is_not_overwritten(self):
        self.document["state"]["desired"]["activationId"] = "pendiente"
        self.assertIn("pendiente", self.speech(self.event("ActivarIntent")))
        self.shadow.update_thing_shadow.assert_not_called()

    def test_busy_motor_rejects_new_cycle(self):
        self.document["state"]["reported"]["servoState"] = "pressing"
        self.assertIn("realizando un ciclo", self.speech(self.event("ActivarIntent")))
        self.shadow.update_thing_shadow.assert_not_called()

    def test_automatic_on_and_off(self):
        for name, expected in [("ActivarAutomaticoIntent", True), ("DesactivarAutomaticoIntent", False)]:
            self.speech(self.event(name))
            payload = json.loads(self.shadow.update_thing_shadow.call_args.kwargs["payload"])
            self.assertEqual(payload["state"], {"desired": {"automatic": expected}})

    def test_conflict_reloads_shadow_then_retries(self):
        self.shadow.update_thing_shadow.side_effect = [aws_error("ConflictException"), {}]
        self.assertIn("Envié", self.speech(self.event("ActivarIntent")))
        self.assertEqual(self.shadow.get_thing_shadow.call_count, 2)

    def test_conflicts_are_bounded(self):
        self.shadow.update_thing_shadow.side_effect = aws_error("ConflictException")
        self.assertIn("cambiando", self.speech(self.event("ActivarIntent")))
        self.assertEqual(self.shadow.update_thing_shadow.call_count, 3)

    def test_missing_shadow_can_receive_first_command(self):
        self.shadow.get_thing_shadow.side_effect = aws_error("ResourceNotFoundException")
        self.speech(self.event("ActivarIntent"))
        payload = json.loads(self.shadow.update_thing_shadow.call_args.kwargs["payload"])
        self.assertNotIn("version", payload)

    def test_sensor_reads_reported_not_desired(self):
        self.document["state"]["desired"]["presence"] = False
        self.assertIn("detectó movimiento", self.speech(self.event("ConsultarSensorIntent")))
        self.shadow.update_thing_shadow.assert_not_called()

    def test_stale_data_not_presented_as_current(self):
        self.document["state"]["reported"]["sampledAt"] -= 60
        for name in ("ConsultarSensorIntent", "ConsultarMotorIntent", "ConsultarAutomaticoIntent"):
            self.assertIn("datos recientes", self.speech(self.event(name)))

    def test_warmup_explained(self):
        self.document["state"]["reported"]["pirReady"] = False
        self.assertIn("estabilizándose", self.speech(self.event("ConsultarSensorIntent")))

    def test_motor_state_and_automatic_queries(self):
        self.assertIn("en reposo", self.speech(self.event("ConsultarMotorIntent")))
        self.assertIn("desactivado", self.speech(self.event("ConsultarAutomaticoIntent")))

    def test_other_skill_is_rejected_before_database(self):
        event = self.event("ActivarIntent")
        event["context"]["System"]["application"]["applicationId"] = "intruso"
        with self.assertRaises(ValueError):
            self.skill.handle(event)
        self.table.get_item.assert_not_called()

    def test_context_user_is_required(self):
        event = self.event("ActivarIntent")
        del event["context"]["System"]["user"]
        with self.assertRaises(ValueError):
            self.skill.handle(event)

    def test_help_stop_and_launch(self):
        self.assertIn("vincula", self.speech(self.event("AMAZON.HelpIntent")))
        response = self.skill.handle(self.event("AMAZON.StopIntent"))
        self.assertTrue(response["response"]["shouldEndSession"])
        event = self.event("unused")
        event["request"]["type"] = "LaunchRequest"
        self.assertIn("activar", self.speech(event))


if __name__ == "__main__":
    unittest.main()
