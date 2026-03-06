# Plan del Portal Ciudadano de Becas RD

Ultima actualizacion: 2026-03-06

## Resumen

Se construira una app web nueva, enfocada al ciudadano, con una identidad visual futurista-premium aplicada sobre un lenguaje claro y orientado al servicio publico. La experiencia tendra tres piezas integradas: portal editorial de entrada, wizard dual de becas y chat asistido por IA.

La v1 se apoyara en el backend Python existente. No habra autenticacion ni persistencia multi-sesion: el estado vivira en memoria del cliente durante la sesion y el usuario podra revisar o descargar un resumen final. El asistente usara el motor local ya disponible en `becas_rd.assistant` y la pre-evaluacion usara `predict_eligibility`.

## Cambios de implementacion

### Arquitectura

- Crear una capa web separada con frontend SPA moderno y una API ligera en Python para exponer el motor actual.
- Mantener el core academico existente como fuente de verdad; no se reescribira la logica de elegibilidad ni del asistente.
- Definir un contrato JSON estable entre frontend y backend para iniciar una sesion de wizard, enviar datos parciales o completos, obtener pre-evaluacion y consultar al asistente con contexto.

### Experiencia de producto

- Disenar una home editorial con narrativa ciudadana, explicacion de tipos de beca, requisitos generales y accesos directos a Evaluacion rapida y Postulacion guiada.
- Implementar un wizard dual:
  - Modo rapido: 4 a 6 pasos orientados a diagnostico inicial y checklist inmediato.
  - Modo completo: flujo continuo con captura de todos los campos relevantes del dataset y requisitos documentales.
- Hacer que ambos modos converjan en una pantalla de resultado con prioridad o probabilidad orientativa, explicacion en lenguaje ciudadano, checklist documental, proximos pasos y acceso al chat con contexto precargado.

### Chat IA

- Crear una interfaz de chat moderna, persistida solo en memoria de sesion, integrada al wizard y al resultado final.
- Permitir que el chat entienda el contexto del usuario actual: tipo de beca, avance del flujo, datos capturados y resultado de pre-evaluacion cuando exista.
- Incluir acciones rapidas como:
  - Que documentos me faltan
  - Soy elegible para beca internacional
  - Explicame mis proximos pasos
- Mantener un tono util y prudente, dejando explicito que la decision oficial no la toma el sistema.

### Direccion visual

- Adoptar una estetica futurista-premium, no institucional plana.
- Usar tipografia de display con personalidad y una familia refinada para lectura.
- Definir una paleta profunda con acentos calidos o metalicos, evitando esquemas genericos.
- Aplicar fondos con textura, capas translucidas y motion intencional en onboarding, transicion de pasos y entrada de mensajes.
- Preservar accesibilidad funcional en movil y escritorio.

## APIs e interfaces publicas

- `POST /api/eligibility/predict`
  - Entrada: perfil del ciudadano con los campos admitidos por `predict_eligibility`.
  - Salida: probabilidad, prioridad, umbral, explicacion y metadatos de resultado.
- `POST /api/assistant/chat`
  - Entrada: `question`, `applicant_context`, `prediction`, `step_context`.
  - Salida: respuesta textual del asistente y, si aplica, referencias documentales resumidas.
- Estado principal del frontend:
  - `wizardMode`: `quick | full`
  - `applicantProfile`
  - `eligibilityResult`
  - `chatMessages`
  - `requiredDocuments`

## Pruebas y escenarios

- Flujo rapido completo con entrada minima valida, calculo de elegibilidad, render de resultado y apertura de chat con contexto heredado.
- Flujo completo con validaciones por paso, navegacion adelante o atras y consolidacion correcta del payload final.
- API con payload valido, campos faltantes, beca internacional con requisitos adicionales y manejo de errores del asistente sin romper la UI.
- Responsive para home, wizard y chat en movil y escritorio.
- Contenido y copy que no prometan adjudicacion oficial.

## Supuestos y decisiones cerradas

- La v1 no crea expedientes oficiales ni envia postulaciones reales; simula y guia el proceso de principio a fin en una sola interaccion.
- No habra cuentas ni reanudacion entre sesiones; el usuario trabajara en una sesion unica y podra exportar o resumir al final.
- El backend de IA sera exclusivamente el motor local actual; no se integrara un LLM externo en esta fase.
- El portal debe ofrecer dos entradas claras: via rapida y via completa.
- Se prioriza una experiencia ciudadano-first con lenguaje simple y resultados explicables.

## Registro de decisiones ejecutadas

- Se implemento la experiencia web sin agregar frameworks de build ni dependencias web externas de runtime: el portal corre como una SPA estatica en `becas_rd/web/` y una API HTTP ligera en `becas_rd/webapp.py`.
- Se mantuvo el core academico existente como fuente de verdad; la UI consume `predict_eligibility` y el asistente documental actual, en vez de duplicar logica.
- El modo rapido se resolvio como un recorrido de 5 pasos que captura todos los campos del modelo, pero con baja friccion; el modo completo amplifica la experiencia con datos de contacto, narrativa y estado documental.
- La region se deriva automaticamente desde la provincia para evitar una pregunta redundante y reducir friccion en el wizard.
- El checklist documental se genera dinamicamente desde reglas locales; en modo rapido muestra preparacion pendiente y en modo completo refleja el estado real marcado por el ciudadano.
- Se decidio mantener la sesion sin autenticacion ni persistencia en backend, pero con descarga de resumen final para no bloquear el MVP por una capa de cuentas.
- El servidor asegura artefactos de modelo de forma automatica: si faltan, reentrena a partir del CSV sintetico existente o genera datos de respaldo.
- La capa de chat acepta contexto del wizard y resultado orientativo para responder con mayor precision, pero sigue mostrando que la decision oficial corresponde al comite.
- Para pruebas automatizadas se valido la capa de aplicacion y los contratos JSON sin depender de sockets locales, porque el sandbox del entorno de desarrollo bloquea `bind()` de puertos.
- Adicionalmente se ejecuto un smoke test real del endpoint `GET /api/health` fuera del sandbox para confirmar que el servidor arranca correctamente en un entorno sin esa restriccion.
