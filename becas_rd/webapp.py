from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import urlparse

import pandas as pd

from .assistant import ScholarshipAssistant
from .data_generation import GenerationConfig, generate_synthetic_data
from .modeling import load_artifacts, predict_eligibility, train_models
from .portal import (
    build_bootstrap_payload,
    build_chat_suggestions,
    build_next_steps,
    build_profile_signals,
    build_required_documents,
    normalize_portal_payload,
    validate_applicant_payload,
)


class PortalApp:
    def __init__(
        self,
        static_dir: str | Path | None = None,
        artifacts_path: str | Path = "artifacts/model_bundle.joblib",
        docs_paths: list[str | Path] | None = None,
    ) -> None:
        self.static_dir = Path(static_dir or Path(__file__).resolve().parent / "web").resolve()
        self.artifacts_path = Path(artifacts_path)
        self.docs_paths = [Path(p) for p in (docs_paths or ["docs/reglamento_becas_rd.md", "docs/faq_becas_rd.md"])]
        self.bootstrap = build_bootstrap_payload()
        self.assistant = ScholarshipAssistant(self.docs_paths)
        self._artifacts = None

    def ensure_artifacts(self) -> Dict[str, Any]:
        if self._artifacts is not None:
            return self._artifacts

        if not self.artifacts_path.exists():
            self.artifacts_path.parent.mkdir(parents=True, exist_ok=True)
            dataset_path = Path("data/synthetic_becas_rd.csv")
            if dataset_path.exists():
                df = pd.read_csv(dataset_path)
            else:
                df = generate_synthetic_data(GenerationConfig(n_samples=2500, random_state=42))
            train_models(df, artifacts_dir=self.artifacts_path.parent)

        self._artifacts = load_artifacts(self.artifacts_path)
        return self._artifacts

    def get_bootstrap(self) -> Dict[str, Any]:
        return self.bootstrap

    def predict(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mode = str(payload.get("mode") or "quick")
        profile = normalize_portal_payload(payload.get("applicant") or payload)
        missing = validate_applicant_payload(profile)
        if missing:
            raise ValueError("Campos requeridos faltantes: " + ", ".join(missing))

        prediction = predict_eligibility(profile, artifacts=self.ensure_artifacts())
        documents = build_required_documents(profile, mode=mode)
        return {
            "profile": profile,
            "prediction": prediction,
            "documents": documents,
            "signals": build_profile_signals(profile, prediction),
            "next_steps": build_next_steps(profile, prediction, mode=mode),
            "disclaimer": "Resultado orientativo. La adjudicacion oficial depende del comite de becas.",
        }

    def answer_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        question = str(payload.get("question") or "").strip()
        if not question:
            raise ValueError("La pregunta no puede estar vacia.")

        applicant = normalize_portal_payload(payload.get("applicant_context"))
        step_context = payload.get("step_context") or {}
        prediction = payload.get("prediction")

        if prediction is None and payload.get("allow_prediction"):
            missing = validate_applicant_payload(applicant)
            if not missing:
                prediction = predict_eligibility(applicant, artifacts=self.ensure_artifacts())

        answer = self.assistant.respond(
            question=question,
            applicant_context=applicant if any(value is not None for value in applicant.values()) else None,
            prediction=prediction,
        )

        retrieval = self.assistant.retrieve(question, top_k=2)
        return {
            "answer": answer,
            "references": [{"source": item.source, "score": round(item.score, 4)} for item in retrieval],
            "suggestions": build_chat_suggestions(
                step_context.get("step_id"),
                applicant=applicant,
                has_result=prediction is not None,
            ),
        }


class PortalHTTPServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], app: PortalApp):
        self.app = app
        super().__init__(server_address, create_handler(app))


def create_handler(app: PortalApp):
    class PortalRequestHandler(BaseHTTPRequestHandler):
        server_version = "PortalBecasRD/1.0"

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(HTTPStatus.NO_CONTENT)
            self._send_common_headers("application/json; charset=utf-8")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/health":
                self._send_json({"status": "ok"})
                return
            if parsed.path == "/api/bootstrap":
                self._send_json(app.get_bootstrap())
                return
            self._serve_static(parsed.path)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            payload = self._read_json_payload()

            try:
                if parsed.path == "/api/eligibility/predict":
                    response = app.predict(payload)
                elif parsed.path == "/api/assistant/chat":
                    response = app.answer_chat(payload)
                else:
                    self._send_json({"error": "Ruta no encontrada."}, status=HTTPStatus.NOT_FOUND)
                    return
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            except Exception as exc:  # pragma: no cover - fallback defensivo
                self._send_json({"error": f"Error interno: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            self._send_json(response)

        def _read_json_payload(self) -> Dict[str, Any]:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length else b"{}"
            try:
                payload = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError("JSON invalido en la solicitud.") from exc
            if not isinstance(payload, dict):
                raise ValueError("El payload debe ser un objeto JSON.")
            return payload

        def _serve_static(self, raw_path: str) -> None:
            relative = raw_path.lstrip("/") or "index.html"
            candidate = (app.static_dir / relative).resolve()
            static_root = app.static_dir.resolve()

            if not str(candidate).startswith(str(static_root)) or not candidate.exists() or candidate.is_dir():
                candidate = static_root / "index.html"

            content_type, _ = mimetypes.guess_type(str(candidate))
            mime = content_type or "application/octet-stream"
            body = candidate.read_bytes()

            self.send_response(HTTPStatus.OK)
            self._send_common_headers(mime)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload: Dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self._send_common_headers("application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_common_headers(self, content_type: str) -> None:
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return PortalRequestHandler


def create_server(host: str = "127.0.0.1", port: int = 8000, app: PortalApp | None = None) -> PortalHTTPServer:
    portal_app = app or PortalApp()
    return PortalHTTPServer((host, port), portal_app)


def run_server(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = create_server(host=host, port=port)
    try:
        print(f"Portal Ciudadano de Becas RD disponible en http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()
