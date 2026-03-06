# Task Plan

Ultima actualizacion: 2026-03-06

Archivo operativo para seguimiento del trabajo. Antes de implementar cambios, revisar este documento y actualizar el estado de las tareas.

## Estado general

- [x] Fase 1: Base web inicial definida y levantada
- [x] Fase 2: Portal editorial ciudadano implementado
- [x] Fase 3: Wizard dual de becas implementado
- [x] Fase 4: Chat IA contextual implementado
- [x] Fase 5: Integracion frontend-backend validada
- [x] Fase 6: QA, accesibilidad y documentacion cerradas

## Tareas

### 1. Base web inicial

- [x] Seleccionar y crear la estructura de la app web y la API ligera sin alterar el core academico existente.
- [x] Definir variables de tema, tipografias, layout base y sistema visual futurista-premium.
- [x] Establecer el contrato inicial de estado para `wizardMode`, `applicantProfile`, `eligibilityResult`, `chatMessages` y `requiredDocuments`.

### 2. Portal editorial ciudadano

- [x] Crear la home principal con hero, narrativa de servicio, tipos de beca y CTA hacia evaluacion rapida y postulacion guiada.
- [x] Incorporar secciones de requisitos generales, beneficios, advertencias eticas y preguntas frecuentes resumidas.
- [x] Ajustar la experiencia responsive del portal para movil y escritorio.

### 3. Wizard dual de becas

- [x] Implementar el acceso dual: modo rapido y modo completo.
- [x] Disenar los pasos del modo rapido para un diagnostico orientativo de baja friccion.
- [x] Disenar los pasos del modo completo para capturar todos los datos relevantes del perfil ciudadano.
- [x] Crear validaciones por paso, navegacion adelante o atras y resumen consolidado previo al resultado.
- [x] Generar checklist documental dinamico segun tipo de beca y contexto del usuario.

### 4. Pre-evaluacion y resultados

- [x] Exponer `predict_eligibility` mediante un endpoint consumible por el frontend.
- [x] Mostrar prioridad, probabilidad, explicacion y proximos pasos en lenguaje ciudadano.
- [x] Permitir exportar o revisar el resumen final de la sesion.

### 5. Chat IA contextual

- [x] Exponer `chat_assistant` mediante un endpoint de chat.
- [x] Construir una interfaz de chat moderna integrada al wizard y al resultado final.
- [x] Conectar el chat al contexto del usuario actual y a su resultado orientativo.
- [x] Incluir prompts de inicio y sugerencias de preguntas frecuentes.

### 6. Calidad

- [x] Cubrir API, wizard rapido, wizard completo y chat con pruebas automatizadas.
- [x] Revisar estados vacios, errores, feedback visual y mensajes de validacion.
- [x] Verificar accesibilidad basica, contraste, foco visible y funcionamiento responsive.
- [x] Actualizar documentacion tecnica y de producto conforme se cierre cada fase.
