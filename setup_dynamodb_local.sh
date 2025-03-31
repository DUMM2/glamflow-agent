#!/bin/bash

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
echo ":small_blue_diamond: Creando la tabla gf-appointment-dev..."
aws dynamodb create-table \
    --table-name gf-appointment-dev \
    --attribute-definitions \
        AttributeName=user_id,AttributeType=N \
        AttributeName=date_appointment,AttributeType=S \
        AttributeName=business_id,AttributeType=N \
    --key-schema \
        AttributeName=user_id,KeyType=HASH \
        AttributeName=date_appointment,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes '[
        {
            "IndexName": "BusinessIndex",
            "KeySchema": [
                {"AttributeName": "business_id", "KeyType": "HASH"}
            ],
            "Projection": {"ProjectionType": "ALL"}
        }
    ]' \
    --endpoint-url http://localhost:8000 \
    --profile local
echo ":white_check_mark: Tabla gf-appointment-dev creada con éxito."

# Crear Tabla Session con Global Secondary Index (GSI)
echo "🔹 Creando la tabla gf-session-dev con índice secundario..."
aws dynamodb create-table \
    --table-name gf-session-dev \
    --attribute-definitions \
        AttributeName=session_id,AttributeType=S \
        AttributeName=init_date_time,AttributeType=S \
        AttributeName=session_status,AttributeType=S \
    --key-schema \
        AttributeName=session_id,KeyType=HASH \
        AttributeName=init_date_time,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --global-secondary-indexes '[
        {
            "IndexName": "StatusIndex",
            "KeySchema": [
                {"AttributeName": "session_status", "KeyType": "HASH"}
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

# Crear tabla Writes mesagges
echo "🔹 Creando la tabla Writes..."
aws dynamodb create-table \
    --table-name writes \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions \
        AttributeName=thread_id_checkpoint_id_checkpoint_ns,AttributeType=S \
        AttributeName=task_id_idx,AttributeType=S \
    --key-schema \
        AttributeName=thread_id_checkpoint_id_checkpoint_ns,KeyType=HASH \
        AttributeName=task_id_idx,KeyType=RANGE \
    --endpoint-url http://localhost:8000 \
    --profile local
echo "✅ Tabla Writes creada con éxito."

# Create tabla Checkpoints
echo "🔹 Creando la tabla checkpoints..."
aws dynamodb create-table \
    --table-name checkpoints \
    --billing-mode PAY_PER_REQUEST \
    --attribute-definitions \
        AttributeName=thread_id,AttributeType=S \
        AttributeName=checkpoint_id,AttributeType=S \
    --key-schema \
        AttributeName=thread_id,KeyType=HASH \
        AttributeName=checkpoint_id,KeyType=RANGE \
    --endpoint-url http://localhost:8000 \
    --profile local
echo "✅ Tabla checkpoints creada con éxito."

# Listar todas las tablas creadas
echo "🔹 Listando todas las tablas en DynamoDB Local..."
aws dynamodb list-tables --endpoint-url http://localhost:8000 --profile local
echo "✅ Listado de tablas completado."

echo "🎉 Todas las tablas fueron creadas exitosamente en DynamoDB Local. 🚀"