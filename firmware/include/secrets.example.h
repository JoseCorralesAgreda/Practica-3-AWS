#pragma once
// Copiar a secrets.h (ignorado por Git). Nunca publicar los valores reales.
constexpr char WIFI_SSID[] = "REEMPLAZAR";
constexpr char WIFI_PASSWORD[] = "REEMPLAZAR";
constexpr char THING_NAME[] = "thing";
constexpr char IOT_ENDPOINT[] = "a2krhgw96q3m1o-ats.iot.us-east-2.amazonaws.com";
constexpr char ROOT_CA[] = R"PEM(
-----BEGIN CERTIFICATE-----
REEMPLAZAR_CON_AMAZON_ROOT_CA_1
-----END CERTIFICATE-----
)PEM";
constexpr char DEVICE_CERT[] = R"PEM(
-----BEGIN CERTIFICATE-----
REEMPLAZAR_CON_CERTIFICADO_DEL_THING
-----END CERTIFICATE-----
)PEM";
constexpr char PRIVATE_KEY[] = R"PEM(
-----BEGIN RSA PRIVATE KEY-----
REEMPLAZAR_CON_CLAVE_PRIVADA_Y_CONSERVAR_SU_CABECERA_REAL
-----END RSA PRIVATE KEY-----
)PEM";
