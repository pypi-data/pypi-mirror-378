# Biblioteca de Iconos para DiagramsOffline

Esta carpeta contiene los iconos para diferentes proveedores de servicios en la nube y tecnologías.

## Estructura de Directorios

```
icons/
├── aws/              # Amazon Web Services
│   ├── compute/      # EC2, Lambda, etc.
│   ├── database/     # RDS, DynamoDB, etc.
│   ├── storage/      # S3, EBS, etc.
│   └── network/      # ELB, CloudFront, etc.
├── gcp/              # Google Cloud Platform
│   ├── compute/      # Compute Engine, etc.
│   ├── database/     # Cloud SQL, etc.
│   └── storage/      # Cloud Storage, etc.
├── k8s/              # Kubernetes
│   ├── compute/      # Pod, Deployment, etc.
│   └── network/      # Service, Ingress, etc.
├── onprem/           # On-Premises
│   ├── compute/      # Server, etc.
│   └── database/     # Database, etc.
└── custom/           # Iconos personalizados
```

## Formato de Iconos

- **Formato**: PNG con transparencia (RGBA)
- **Tamaño**: 64x64 píxeles (se pueden escalar automáticamente)
- **Colores**: Siguiendo los colores oficiales de cada proveedor

## Añadir Nuevos Iconos

1. Guarda el icono en la carpeta apropiada
2. Usa nombres descriptivos en minúsculas con guiones bajos
3. Actualiza el archivo `nodes.py` con la nueva clase de nodo
4. Especifica la ruta del icono en el constructor

## Iconos por Implementar

### AWS (Alta Prioridad)
- [ ] EC2 (compute/ec2.png)
- [ ] Lambda (compute/lambda.png)
- [ ] RDS (database/rds.png)
- [ ] S3 (storage/s3.png)
- [ ] ELB (network/elb.png)

### GCP
- [ ] Compute Engine (compute/compute_engine.png)
- [ ] Cloud SQL (database/cloud_sql.png)
- [ ] Cloud Storage (storage/cloud_storage.png)

### Kubernetes
- [ ] Pod (compute/pod.png)
- [ ] Service (network/service.png)
- [ ] Deployment (compute/deployment.png)

### On-Premises
- [ ] Server (compute/server.png)
- [ ] Database (database/database.png)
- [ ] Load Balancer (network/load_balancer.png)

## Fuentes de Iconos

1. **Iconos oficiales** (cuando sea posible)
2. **Feather Icons** - Para iconos genéricos
3. **Material Design Icons** - Para complementar
4. **Iconos personalizados** - Creados con las herramientas de diseño

## Notas de Implementación

- Los iconos se cargan automáticamente por el `PillowRenderer`
- Si un icono no existe, se usa un placeholder rectangular con color
- Los iconos se redimensionan automáticamente según el tamaño del nodo
- Soporte para descarga automática de iconos desde URLs (función `download_icon`)