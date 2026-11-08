"""Backend de una skill personalizada. Handler: lambda_function.lambda_handler."""
import json
import logging
import os
import re
import time
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


class AmbientadorSkill:
    """Resuelve al usuario en DynamoDB y controla exclusivamente el Shadow clásico."""

    def __init__(self, table, iot, shadow, skill_id):
        self.table = table
        self.iot = iot
        self.shadow = shadow
        self.skill_id = skill_id

    @staticmethod
    def respond(text, end=False):
        response = {
            "outputSpeech": {"type": "PlainText", "text": text},
            "shouldEndSession": end,
        }
        if not end:
            response["reprompt"] = {
                "outputSpeech": {"type": "PlainText", "text": "Puedes pedir ayuda o decir salir."}
            }
        return {"version": "1.0", "response": response}

    def get_shadow(self, thing):
        try:
            result = self.shadow.get_thing_shadow(thingName=thing)
            return json.loads(result["payload"].read())
        except ClientError as error:
            if error.response["Error"]["Code"] == "ResourceNotFoundException":
                return {"state": {}}
            raise

    def command(self, thing, request_id=None, automatic=None):
        # Versionado evita sobrescribir otro comando concurrente. Un Shadow es
        # estado persistente, no una cola: se admite una activación pendiente.
        for _ in range(3):
            document = self.get_shadow(thing)
            state = document.get("state", {})
            desired = state.get("desired", {})
            reported = state.get("reported", {})
            if request_id:
                if desired.get("activationId") == request_id:
                    return self.respond("Esta solicitud ya fue enviada al ambientador.")
                pending = desired.get("activationId")
                if pending and pending != reported.get("activationId"):
                    return self.respond("Ya hay una activación pendiente. Espera a que el dispositivo la procese.")
                if reported.get("servoState") in ("pressing", "returning"):
                    return self.respond("El ambientador está realizando un ciclo. Espera un momento.")
                changes = {"activationId": request_id}
            else:
                changes = {"automatic": automatic}
            payload = {"state": {"desired": changes}}
            if "version" in document:
                payload["version"] = document["version"]
            try:
                self.shadow.update_thing_shadow(thingName=thing, payload=json.dumps(payload).encode())
                text = "Envié la activación al ambientador."
                if automatic is not None:
                    text = "Solicité activar el modo automático." if automatic else "Solicité desactivar el modo automático."
                return self.respond(text + " Si está desconectado, la aplicará al reconectarse.")
            except ClientError as error:
                if error.response["Error"]["Code"] != "ConflictException":
                    raise
        return self.respond("El estado está cambiando. Inténtalo nuevamente en unos segundos.")

    def handle(self, event):
        system = event.get("context", {}).get("System", {})
        if not self.skill_id or system.get("application", {}).get("applicationId") != self.skill_id:
            raise ValueError("Skill no autorizada")
        user_id = system.get("user", {}).get("userId")
        if not user_id:
            raise ValueError("Falta context.System.user.userId")
        request = event.get("request", {})
        if request.get("type") == "SessionEndedRequest":
            return {"version": "1.0", "response": {}}
        # Lectura consistente en cada solicitud, sin depender de la sesión Alexa.
        binding = self.table.get_item(Key={"userId": user_id}, ConsistentRead=True).get("Item")
        if request.get("type") == "LaunchRequest":
            if not binding:
                return self.respond("Bienvenido. Primero di: vincula mi ambientador con thing.")
            return self.respond("Puedes activar el ambientador, consultar presencia o cambiar el modo automático.")
        if request.get("type") != "IntentRequest":
            return self.respond("No pude interpretar esa solicitud. Puedes pedir ayuda.")
        intent = request.get("intent", {})
        name = intent.get("name", "")
        if name in ("AMAZON.StopIntent", "AMAZON.CancelIntent"):
            return self.respond("Hasta luego.", end=True)
        if name in ("AMAZON.HelpIntent", "AMAZON.FallbackIntent"):
            return self.respond("Di vincula mi ambientador con thing; activa el ambientador; hay movimiento; "
                                "cuál es el estado del motor; activa o desactiva el modo automático; o desvincula mi ambientador.")
        if name == "VincularIntent":
            slot = intent.get("slots", {}).get("thingName", {})
            thing = slot.get("value", "").strip()
            for authority in slot.get("resolutions", {}).get("resolutionsPerAuthority", []):
                if authority.get("status", {}).get("code") == "ER_SUCCESS_MATCH":
                    thing = authority["values"][0]["value"]["name"]
                    break
            if not re.fullmatch(r"[A-Za-z0-9:_-]{1,128}", thing):
                return self.respond("Indica un nombre válido. Por ejemplo: vincula mi ambientador con thing.")
            try:
                self.iot.describe_thing(thingName=thing)
            except ClientError as error:
                if error.response["Error"]["Code"] == "ResourceNotFoundException":
                    return self.respond("Ese objeto no existe. Revisa su nombre e intenta vincularlo otra vez.")
                raise
            self.table.put_item(Item={
                "userId": user_id, "thingName": thing,
                "fechaVinculacion": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
            return self.respond("Vinculé tu ambientador. Esta vinculación reemplaza cualquier vinculación anterior.")
        if name == "DesvincularIntent":
            self.table.delete_item(Key={"userId": user_id})
            return self.respond("Eliminé tu vinculación. El modo automático del dispositivo no cambia.")
        if not binding:
            return self.respond("No tienes un objeto vinculado. Di: vincula mi ambientador con thing.")
        thing = binding["thingName"]
        if name == "ActivarIntent":
            request_id = request.get("requestId", "")
            if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
                return self.respond("La solicitud no tiene un identificador válido. Inténtalo otra vez.")
            return self.command(thing, request_id=request_id)
        if name in ("ActivarAutomaticoIntent", "DesactivarAutomaticoIntent"):
            return self.command(thing, automatic=name == "ActivarAutomaticoIntent")
        if name not in ("ConsultarSensorIntent", "ConsultarMotorIntent", "ConsultarAutomaticoIntent"):
            return self.respond("No reconozco ese comando. Puedes pedir ayuda.")
        document = self.get_shadow(thing)
        reported = document.get("state", {}).get("reported", {})
        timestamp = reported.get("sampledAt", 0)
        if not isinstance(timestamp, (int, float)) or time.time() - timestamp > 45 or timestamp > time.time() + 10:
            return self.respond("No tengo datos recientes del dispositivo. Comprueba su conexión.")
        if name == "ConsultarSensorIntent":
            if not reported.get("pirReady", False):
                return self.respond("El sensor está estabilizándose. Espera un minuto desde el encendido.")
            if not isinstance(reported.get("presence"), bool):
                return self.respond("Todavía no tengo una lectura válida del sensor.")
            text = "La última lectura detectó movimiento." if reported["presence"] else "La última lectura no detectó movimiento."
            return self.respond(text + " El PIR no confirma la presencia de una persona inmóvil.")
        if name == "ConsultarAutomaticoIntent":
            if not isinstance(reported.get("automatic"), bool):
                return self.respond("Todavía no tengo un estado confirmado del modo automático.")
            return self.respond("El modo automático reportado está " + ("activado." if reported["automatic"] else "desactivado."))
        states = {"idle": "en reposo", "pressing": "en la fase de activación", "returning": "regresando al reposo"}
        state = states.get(reported.get("servoState"))
        if state is None:
            return self.respond("Todavía no tengo un estado válido del motor.")
        return self.respond(f"El controlador reporta el motor {state}. El servo no tiene realimentación de posición.")


_skill = None


def lambda_handler(event, context):
    """Boto3 usa el rol de ejecución de Lambda; no hay access keys en el código."""
    global _skill
    try:
        if _skill is None:
            region = os.environ["IOT_REGION"]
            _skill = AmbientadorSkill(
                boto3.resource("dynamodb").Table(os.environ["BINDINGS_TABLE"]),
                boto3.client("iot", region_name=region),
                boto3.client("iot-data", region_name=region, endpoint_url=os.environ["IOT_DATA_ENDPOINT"]),
                os.environ["ALEXA_SKILL_ID"],
            )
        return _skill.handle(event)
    except (ClientError, BotoCoreError):
        # No registrar eventos completos, userId, certificados ni credenciales.
        LOGGER.exception("Fallo al acceder a un servicio AWS")
        return AmbientadorSkill.respond("No pude acceder al servicio. Inténtalo de nuevo en unos segundos.")
