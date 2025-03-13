#!/bin/bash

echo "🔹 Descargando Docker DynamoDB Local..."
docker pull amazon/dynamodb-local

echo "🔹 Configurando el perfil local en AWS CLI..."
aws configure --profile local

echo "✅ Configuración completada."

# Crear Tabla User
echo "🔹 Creando la tabla gf-user-dev..."
aws dynamodb create-table \
    --table-name gf-user-dev \
    --attribute-definitions AttributeName=user_id,AttributeType=N \
    --key-schema AttributeName=user_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000 \
    --profile local
echo "✅ Tabla gf-user-dev creada con éxito."

# Crear Tabla Appointment
echo "🔹 Creando la tabla gf-appointment-dev..."
aws dynamodb create-table \
    --table-name gf-appointment-dev \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=N \
        AttributeName=date_time,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=date_time,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000 \
    --profile local
echo "✅ Tabla gf-appointment-dev creada con éxito."

# Crear Tabla Session con Global Secondary Index (GSI)
echo "🔹 Creando la tabla gf-session-dev con índice secundario..."
aws dynamodb create-table \
    --table-name gf-session-dev \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=N \
        AttributeName=init_date_time,AttributeType=S \
        AttributeName=status,AttributeType=S \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=init_date_time,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes '[
        {
            "IndexName": "StatusIndex",
            "KeySchema": [
                {"AttributeName": "status", "KeyType": "HASH"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ]' \
    --endpoint-url http://localhost:8000 \
    --profile local
echo "✅ Tabla gf-session-dev creada con éxito."

# Crear Tabla Business
echo "🔹 Creando la tabla gf-business-dev..."
aws dynamodb create-table \
    --table-name gf-business-dev \
    --attribute-definitions AttributeName=business_id,AttributeType=N \
    --key-schema AttributeName=business_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --endpoint-url http://localhost:8000 \
    --profile local
echo "✅ Tabla gf-business-dev creada con éxito."

# Listar todas las tablas creadas
echo "🔹 Listando todas las tablas en DynamoDB Local..."
aws dynamodb list-tables --endpoint-url http://localhost:8000 --profile local
echo "✅ Listado de tablas completado."

echo "🎉 Todas las tablas fueron creadas exitosamente en DynamoDB Local. 🚀"
